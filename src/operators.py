import bpy
import traceback

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

import xml.etree.ElementTree as ET
import zipfile

import lib3mf
from lib3mf import get_wrapper


def _build_name_map(model):
    """
    Build a mapping from resource ID -> human-ish name using build items +
    object properties. This tries, in order:
      1. Object name
      2. Object part number
      3. Build item part number
    """
    names_by_res_id = {}

    try:
        build_it = model.GetBuildItems()
    except Exception:
        return names_by_res_id  # no build items? fine, just fall back later

    count = build_it.Count()
    for _ in range(count):
        build_it.MoveNext()
        item = build_it.GetCurrent()
        obj = item.GetObjectResource()

        # Resource ID that we can later match against mesh objects
        try:
            res_id = obj.GetResourceID()
        except Exception:
            try:
                res_id = obj.GetUniqueResourceID()
            except Exception:
                continue

        # Only set a name once per resource ID – first hit wins
        if res_id in names_by_res_id:
            continue

        name = ""
        try:
            name = obj.GetName() or ""
        except Exception:
            pass

        if not name:
            try:
                name = obj.GetPartNumber() or ""
            except Exception:
                pass

        if not name:
            try:
                name = item.GetPartNumber() or ""
            except Exception:
                pass

        if name:
            names_by_res_id[res_id] = name

    return names_by_res_id


def _load_slic3r_object_names_from_attachment(model) -> dict[int, str]:
    """
    Use lib3mf's attachment API to load MetaData/Slic3r_PE_model.config,
    parse it, and return {object_id: name}.
    """

    attachment = None

    # 1) Try the canonical path first
    try:
        attachment = model.FindAttachment("MetaData/Slic3r_PE_model.config")
    except Exception:
        attachment = None

    # 2) If that fails, scan all attachments and match by filename
    if attachment is None:
        try:
            count = model.GetAttachmentCount()
        except Exception:
            count = 0

        for i in range(count):
            att = model.GetAttachment(i)
            path = att.GetPath()  # e.g. "MetaData/Slic3r_PE_model.config"
            print(f"[3MF IO] Attachment[{i}] path: {path!r}")
            if path and path.lower().endswith("slic3r_pe_model.config"):
                attachment = att
                break

    if attachment is None:
        print("[3MF IO] No Slic3r_PE_model.config attachment found")
        return {}

    # 3) Read attachment payload through lib3mf
    try:
        raw = attachment.WriteToBuffer()
    except TypeError:
        size = attachment.GetStreamSize()
        buf = bytearray(size)
        attachment.WriteToBuffer(buf)
        raw = bytes(buf)

    if isinstance(raw, list):
        data = bytes(raw)
    else:
        data = bytes(raw)

    text = data.decode("utf-8", errors="replace")

    return _parse_slic3r_config_xml(text)


def _load_slic3r_object_names_from_zip(path: str) -> dict[int, str]:
    """
    Fallback: use Python's zipfile module to load MetaData/Slic3r_PE_model.config
    when it is not exposed as a 3MF attachment (Prusa/Slic3r does this).
    """
    try:
        with zipfile.ZipFile(path, "r") as zf:
            target_name = None
            for name in zf.namelist():
                lower = name.lower()
                if lower.endswith("slic3r_pe_model.config"):
                    target_name = name
                    break

            if not target_name:
                print("[3MF IO] No Slic3r_PE_model.config found via zipfile either")
                return {}

            with zf.open(target_name) as f:
                text = f.read().decode("utf-8", errors="replace")

        return _parse_slic3r_config_xml(text)
    except Exception as e:
        print(f"[3MF IO] zipfile fallback failed: {e!r}")
        traceback.print_exc()
        return {}


def _parse_slic3r_config_xml(text: str) -> dict[int, str]:
    """
    Parse the content of Slic3r_PE_model.config and return {object_id: name}.
    """
    root = ET.fromstring(text)
    id_to_name: dict[int, str] = {}

    for obj_elem in root.findall(".//object"):
        obj_id_str = obj_elem.get("id")
        if not obj_id_str:
            continue

        name = None

        # Prefer <metadata type="object" key="name" ...>
        for md in obj_elem.findall("metadata"):
            if md.get("type") == "object" and md.get("key") == "name":
                name = md.get("value")
                break

        # Fallback: volume-level metadata
        if not name:
            vol = obj_elem.find("volume")
            if vol is not None:
                for md in vol.findall("metadata"):
                    if md.get("key") == "name":
                        name = md.get("value")
                        break

        if name:
            try:
                obj_id = int(obj_id_str)
            except ValueError:
                continue
            id_to_name[obj_id] = name

    print(f"[3MF IO] Parsed Slic3r names: {id_to_name}")
    return id_to_name


def _load_slic3r_object_names(path: str, model) -> dict[int, str]:
    """
    Hybrid loader:
      1. Try lib3mf attachments (for 3MFs that register the config as an attachment).
      2. If that yields nothing, fall back to zipfile direct access.
    """
    names = _load_slic3r_object_names_from_attachment(model)
    if names:
        return names

    print("[3MF IO] Falling back to zipfile for Slic3r names")
    return _load_slic3r_object_names_from_zip(path)


def _name_for_mesh(mesh_obj, names_by_res_id, default_index):
    """
    Pick the "best" name for this mesh resource:
      1. From names_by_res_id (build items + slicer metadata)
      2. From the object's own Name
      3. From the object's PartNumber
      4. Fallback to a generic 3MF_Mesh_N
    """
    res_id = None
    try:
        res_id = mesh_obj.GetResourceID()
    except Exception:
        try:
            res_id = mesh_obj.GetUniqueResourceID()
        except Exception:
            pass

    if res_id is not None and res_id in names_by_res_id:
        return names_by_res_id[res_id]

    try:
        name = (mesh_obj.GetName() or "").strip()
        if name:
            return name
    except Exception:
        pass

    try:
        part = (mesh_obj.GetPartNumber() or "").strip()
        if part:
            return part
    except Exception:
        pass

    return f"3MF_Mesh_{default_index}"


class SHADOWMOOSE_OT_import_3mf(bpy.types.Operator, ImportHelper):
    """Import a 3MF file and create Blender meshes from it."""
    bl_idname = "import_scene.shadowmoose_3mf_io"
    bl_label = "3MF (3MF IO)"

    filename_ext = ".3mf"
    filter_glob: StringProperty(
        default="*.3mf",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        path = self.filepath

        try:
            wrapper = get_wrapper()
            model = wrapper.CreateModel()

            reader = model.QueryReader("3mf")
            reader.ReadFromFile(path)

            # Slic3r/Prusa-specific names (via attachment or zipfile)
            slic3r_names = _load_slic3r_object_names(path, model)

            # Build base name map from build items
            names_by_res_id = _build_name_map(model)

            # Overlay Slic3r names so they win if they exist
            # key:  3MF object ID (res_id)
            # value: "Cthuwu.stl", etc.
            for obj_id, name in slic3r_names.items():
                names_by_res_id[obj_id] = name

            print(f"[3MF IO] Final name map (res_id -> name): {names_by_res_id}")

            mesh_it = model.GetMeshObjects()

            imported_count = 0
            scene = context.scene
            collection = scene.collection

            mesh_count = mesh_it.Count()
            print(f"[3MF IO] Mesh object count: {mesh_count}")

            for _ in range(mesh_count):
                mesh_it.MoveNext()
                mesh3mf = mesh_it.GetCurrentMeshObject()

                name = _name_for_mesh(mesh3mf, names_by_res_id, imported_count)

                verts = [
                    (v.Coordinates[0], v.Coordinates[1], v.Coordinates[2])
                    for v in mesh3mf.GetVertices()
                ]

                tri_count = mesh3mf.GetTriangleCount()
                faces = []
                for i in range(tri_count):
                    tri = mesh3mf.GetTriangle(i)
                    a, b, c = tri.Indices[0:3]
                    faces.append((a, b, c))

                if not verts or not faces:
                    print(f"[3MF IO] Skipping empty mesh '{name}'")
                    continue

                me = bpy.data.meshes.new(name)
                me.from_pydata(verts, [], faces)
                me.validate(verbose=False)
                me.update()

                obj = bpy.data.objects.new(name, me)
                collection.objects.link(obj)

                try:
                    res_id_debug = mesh3mf.GetResourceID()
                except Exception:
                    res_id_debug = None

                print(
                    f"[3MF IO] Imported mesh '{name}' "
                    f"(res_id={res_id_debug}) with "
                    f"{len(verts)} verts, {len(faces)} tris"
                )
                imported_count += 1

            self.report({'INFO'}, f"Imported {imported_count} mesh(es) from {path}")
            print(f"[3MF IO] Done importing {imported_count} mesh(es) from {path}")
            return {'FINISHED'}

        except Exception as e:
            print(f"[3MF IO] Error importing 3MF: {e!r}")
            traceback.print_exc()
            self.report({'ERROR'}, f"3MF import failed: {e!r}")
            return {'CANCELLED'}


# ----- Menu integration ----------------------------------------------------


def menu_func_import(self, context):
    """Add our import operator to File > Import."""
    self.layout.operator(
        SHADOWMOOSE_OT_import_3mf.bl_idname,
        text="3MF (.3mf) (3MF IO)",
    )


def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
