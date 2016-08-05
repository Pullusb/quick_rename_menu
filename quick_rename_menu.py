bl_info = {
    "name": "Quick Rename",
    "description": "Pop a menu with alt+N to quickly rename active object",
    "author": "Samuel Bernou",
    "version": (1, 0, 1),
    "blender": (2, 77, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }


import bpy, re


###---FUNCTIONS---

def changeNameSide(name):
    '''Return the name side switched if already ends by a side (else return False)'''
    sidext = ['.L', '.R', '_L', '_R']
    if name[-2:] in sidext:
        if name[-1:] == 'L':
            return(name[:-1] + 'R')
        elif name[-1:] == 'R':
            return(name[:-1] + 'L')
    else:
        return (False)

def checkExists(name, bname, change, new):
    if bname: #check bone
        if bpy.data.armatures[name].bones.get(new):
            return(False)#bone exists
        else: # name available
            if change:
                bpy.context.active_bone.name = new
            else:
                return(new)
    else: #check object
        # print ("CHECK EXIST", new)
        if bpy.data.objects.get(new):
            return(False)#object exists
        else: # name available
            if change:
                bpy.context.active_object.name = new
            else:
                return(new)

def defineBase(name,bname):
    if bname:
        return (bname)
    else:
        return (name)

####---RULES---

def DeleteNumber(name, bname, change = False):
    '''object.001 > object'''
    base = defineBase(name,bname)
    number = re.search('\.\d{3}$',base)
    if number:
        # print (number.group() )
        new = re.sub('\.\d{3}$', '', base)
        return(checkExists(name, bname, change, new))

class DeleteNumberOP(bpy.types.Operator):
    bl_idname = "name.delete_number"
    bl_label = "Delete Number"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if context.active_object.type == 'ARMATURE' and context.active_object.mode in {'EDIT', 'POSE'}:
            DeleteNumber(context.active_object.name, context.active_bone.name, change = True)
        else:
            DeleteNumber(context.active_object.name, False, change = True)
            return {"FINISHED"}


def mirrorExt(name, bname, change = False):
    '''object.L > object.R'''
#    side = re.search('[\._][LR]$',name)
#    if side:
#        print (side.group() )
    base = defineBase(name,bname)
    opposite = changeNameSide(base)
    if opposite:
        return(checkExists(name, bname, change, opposite))

class mirrorExtOP(bpy.types.Operator):
    bl_idname = "name.mirror_ext"
    bl_label = "Mirror name extension"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if context.active_object.type == 'ARMATURE' and context.active_object.mode in {'EDIT', 'POSE'}:
            mirrorExt(context.active_object.name, context.active_bone.name, change = True)
        else:
            mirrorExt(context.active_object.name, False, change = True)
        return {"FINISHED"}

def LeftFromNumber(name, bname, change = False):
    '''object.001 > object.L'''
    base = defineBase(name,bname)
    number = re.search('\.\d{3}$',base)
    if number:
        # print (number.group() )
        new = re.sub('\.\d{3}$', '', base)
        new += '.L'
        return(checkExists(name, bname, change, new))

class LeftFromNumberOP(bpy.types.Operator):
    bl_idname = "name.mirror_from_left"
    bl_label = "Mirror name extension"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if context.active_object.type == 'ARMATURE' and context.active_object.mode in {'EDIT', 'POSE'}:
            LeftFromNumber(context.active_object.name, context.active_bone.name, change = True)
        else:
            LeftFromNumber(context.active_object.name, False, change = True)
        return {"FINISHED"}


def mirrorSideFromNumber(name, bname, change = False):
    '''object.L.001 > object.R'''
    base = defineBase(name,bname)
    number = re.search('[\._][L,R]\.\d{3}$',base)
    if number:
        # print (number.group() )
        new = re.sub('\.\d{3}$', '', base)
        new = changeNameSide(new)
        return(checkExists(name, bname, change, new))

class mirrorSideFromNumberOP(bpy.types.Operator):
    bl_idname = "name.mirror_side_from_num"
    bl_label = "Mirror name extension"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if context.active_object.type == 'ARMATURE' and context.active_object.mode in {'EDIT', 'POSE'}:
            mirrorSideFromNumber(context.active_object.name, context.active_bone.name, change = True)
        else:
            mirrorSideFromNumber(context.active_object.name, False, change = True)
        return {"FINISHED"}



###---MENU---

class PopQuickRenameMenu(bpy.types.Menu):
    bl_idname = "view3d.pop_quick_rename_menu"
    bl_label = "quick rename"

    def draw(self, context):
        layout = self.layout
        #layout.operator_context = 'INVOKE_REGION_WIN'
        #layout.operator("transform.translate", 'Grab', icon='MOD_SUBSURF')

        ob = context.active_object
        name = ob.name

        if ob.type == 'ARMATURE' and ob.mode in {'EDIT', 'POSE'}:
            b = context.active_bone
            if b:
                row = layout.row()
                #row.label(text="", icon='BONE_DATA')
                row.prop(b, "name", text="", icon='BONE_DATA')
                bone = b.name

        else:
            row = layout.row()
            # row.label(text="obj name :", icon='OBJECT_DATA')
            # row = layout.row(align=True)
            row.prop(ob, "name", text="", icon='OBJECT_DATA')
            bone = False

        # row.label(text='change to: ' , icon=OUTLINER_OB_MESH)
        row = layout.row()
        row.separator()

        rNum = DeleteNumber(name, bone)
        if rNum:
            row = layout.row()
            row.operator('name.delete_number', rNum, icon='FORWARD')

        rSide = mirrorExt(name, bone)
        if rSide:
            row = layout.row()
            row.operator('name.mirror_ext', rSide, icon='FORWARD')

        rLeft = LeftFromNumber(name, bone)
        if rLeft:
            row = layout.row()
            row.operator('name.mirror_from_left', rLeft, icon='FORWARD')

        rSideExt = mirrorSideFromNumber(name, bone)
        if rSideExt:
            row = layout.row()
            row.operator('name.mirror_side_from_num', rSideExt, icon='FORWARD')

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
    if not bpy.app.background:
        register_keymaps()
    bpy.utils.register_module(__name__)

def unregister():
    if not bpy.app.background:
        unregister_keymaps()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
