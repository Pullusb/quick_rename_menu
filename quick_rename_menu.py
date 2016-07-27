bl_info = {
    "name": "Quick Rename",
    "description": "Pop a menu with alt+N to quickly rename active object",
    "author": "Samuel Bernou",
    "version": (1, 0, 0),
    "blender": (2, 77, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }


import bpy, re


def regNumber(name, change = False):

    number = re.search('\.\d{3}$',name)
    if number:
        # print (number.group() )
        new = re.sub('\.\d{3}$', '', name)
        if bpy.data.objects.get(new):
            #print ('object exist')
            return(False)
        else:
            if change:
                bpy.context.object.name = new
            else:
                return(new)


def regSide(name, change = False):
#    side = re.search('[\._][LR]$',name)
#    if side:
#        print (side.group() )

    sidext = ['.L', '.R', '_L', '_R']
    if name[-2:] in sidext:
        if name[-1:] == 'L':
            opposite = name[:-1] + 'R'
        elif name[-1:] == 'R':
            opposite = name[:-1] + 'L'

        if bpy.data.objects.get(opposite):
            # print ('object name exist')
            return(False)
        else:
            if change:
                bpy.context.object.name = opposite
            else:
                return(opposite)


class mirrorExt(bpy.types.Operator):
    bl_idname = "name.mirror_ext"
    bl_label = "Mirror name extension"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        regSide(context.object.name, change = True)
        return {"FINISHED"}


class DeleteNumber(bpy.types.Operator):
    bl_idname = "name.delete_number"
    bl_label = "Delete Number"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        regNumber(context.object.name, change = True)
        return {"FINISHED"}


class PopQuickRenameMenu(bpy.types.Menu):
    bl_idname = "view3d.pop_quick_rename_menu"
    bl_label = "quick rename"

    def draw(self, context):
        layout = self.layout
        #layout.operator_context = 'INVOKE_REGION_WIN'
        #layout.operator("transform.translate", 'Grab', icon='MOD_SUBSURF')
        ob = context.active_object
        name = ob.name

        row = layout.row()
#        row.label(text="obj name :", icon='OBJECT_DATA')
#        row = layout.row(align=True)
        row.prop(ob, "name", text="")

        if ob.type == 'ARMATURE' and ob.mode in {'EDIT', 'POSE'}:
            bone = context.active_bone
            if bone:
                row = layout.row()
                row.label(text="", icon='BONE_DATA')
                row.prop(bone, "name", text="")

        # row.label(text='change to: ' , icon=OUTLINER_OB_MESH)

        rNum = regNumber(name)
        # print(rNum)

        if rNum:
            row = layout.row()
            row.operator('name.delete_number', rNum, icon='FORWARD')

        rSide = regSide(name)
        # print(rSide)

        if rSide:
            row = layout.row()
            row.operator('name.mirror_ext', rSide, icon='FORWARD')


addon_keymaps = []
def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name = "3D View", space_type = "VIEW_3D")
    # keymap items here
    kmi = km.keymap_items.new('wm.call_menu', type = "N", value = "PRESS", alt = True)
    kmi.properties.name = 'view3d.pop_quick_rename_menu'

    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()



def register():
    register_keymaps()
    bpy.utils.register_module(__name__)

def unregister():
    unregister_keymaps()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
