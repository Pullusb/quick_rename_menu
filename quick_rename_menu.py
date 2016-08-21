bl_info = {
    "name": "Quick Rename",
    "description": "Pop a menu to quickly rename active object or bone",
    "author": "Samuel Bernou",
    "version": (1, 0, 2),
    "blender": (2, 77, 0),
    "location": "View3D > alt+N shortcut",
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


def changeDataName(new):
    '''change active object data name if option checked in addon preferences'''
    if bpy.context.user_preferences.addons[__name__].preferences.RN_renameData:
        if bpy.context.active_object.data.users == 1 or bpy.context.user_preferences.addons[__name__].preferences.RN_renameLinked:
            if bpy.data.meshes.get(new):
                print('object data', bpy.context.active_object.data.name,
                    'was not renamed:\n', new, "name conflict (already exists in data")
            else:
                bpy.context.active_object.data.name = new
        else :
            print ('object data', bpy.context.active_object.data.name, 'has more tha n 1 user and was not renamed')

def checkExists(name, bname, change, new):
    '''
    Check if passed 'new' name already exists in objects (or armature if bname is passed)
    Return False if name is taken
    Apply new name to object if new is available and 'change' is True
    '''
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
                #rename data if check in addon pref by user
                changeDataName(new)
            else:
                return(new)

def defineBase(name,bname):
    '''Return bname if bone name is not none, else return name'''
    if bname:
        return (bname)
    else:
        return (name)

####---RULES--- (functions followed by class operators)


##--renumbering

def DeleteNumber(name, bname, change = False):
    '''object.001 > object'''
    if bname:#Function Raise an error with bones !
        return(False)
    base = defineBase(name,bname)
    number = re.search('\.\d{3}$',base)

    if number:
        new = base[:-len(number.group(0))]#re.sub('\.\d{3}$', '', base)
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


def IncrementPreviousNum(name, bname, change = False):
    '''object_02.001 > object_03'''
    # if bname:#Function Raise an error with bones !
    #     return(False)
    base = defineBase(name,bname)
    num = re.search('(\d{1,4})\.\d{3}$',base)
     
    if num:
        prevNum = num.group(1)
        increment = str(int(prevNum)+1).zfill(len(prevNum))
        new = base[:-len(num.group(0))]#Faster than: re.sub('\d{1,4}\.\d{3}$', '', base)
        new += increment
        return(checkExists(name, bname, change, new))

class IncrementPreviousNumOP(bpy.types.Operator):
    bl_idname = "name.increment_previous_num"
    bl_label = "Increment previous number"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if context.active_object.type == 'ARMATURE' and context.active_object.mode in {'EDIT', 'POSE'}:
            IncrementPreviousNum(context.active_object.name, context.active_bone.name, change = True)
        else:
            IncrementPreviousNum(context.active_object.name, False, change = True)
            return {"FINISHED"}

##--side

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
        new = base[:-len(number.group(0))]#re.sub('\.\d{3}$', '', base)
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


##--bone specific

def AddRoot(name, bname, change = False):
    '''object.L.001 > object.R'''
    base = defineBase(name,bname)
    if not bname:#armature only
        return (False)
    new = 'root'
    pos = 'Root'
    if not checkExists(name, bname, False, pos):#test if Root with maj exist (return False if any)
        return (False)
    return(checkExists(name, bname, change, new))

class AddRootOP(bpy.types.Operator):
    bl_idname = "name.add_root"
    bl_label = "Name bone root"
    bl_description = "change to this name"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if context.active_object.type == 'ARMATURE' and context.active_object.mode in {'EDIT', 'POSE'}:
            AddRoot(context.active_object.name, context.active_bone.name, change = True)
        # else:
        #     mirrorSideFromNumber(context.active_object.name, False, change = True)
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
        if ob.library:#if object is linked, dont do anything
            row = layout.row()
            row.label('Object is linked!')
        else:

            if ob.type == 'ARMATURE' and ob.mode in {'EDIT', 'POSE'}:
                b = context.active_bone
                if b:
                    row = layout.row()
                    #row.label(text="", icon='BONE_DATA')
                    row.prop(b, "name", text="", icon='BONE_DATA')
                    bone = b.name
                    #update to refresh name base (else need to leave bone edit and return)
                    ob.update_from_editmode()

            else:
                row = layout.row()
                # row.label(text="obj name :", icon='OBJECT_DATA')
                # row = layout.row(align=True)
                row.prop(ob, "name", text="", icon='OBJECT_DATA')
                bone = False


            ##list of rules (uncomment all following to supress propositions)

            # row.label(text='change to: ' , icon=OUTLINER_OB_MESH)
            row = layout.row()
            row.separator()

            rNum = DeleteNumber(name, bone)
            if rNum:
                layout.row().operator('name.delete_number', rNum, icon='FORWARD')

            rIncPrevNum = IncrementPreviousNum(name, bone)
            if rIncPrevNum: 
                layout.row().operator('name.increment_previous_num', rIncPrevNum, icon='FORWARD')

            rSide = mirrorExt(name, bone)
            if rSide:
                layout.row().operator('name.mirror_ext', rSide, icon='FORWARD')

            rLeft = LeftFromNumber(name, bone)
            if rLeft:
                layout.row().operator('name.mirror_from_left', rLeft, icon='FORWARD')

            rSideExt = mirrorSideFromNumber(name, bone)
            if rSideExt:
                layout.row().operator('name.mirror_side_from_num', rSideExt, icon='FORWARD')

            rRootBone = AddRoot(name, bone)
            if rRootBone:
                layout.row().operator('name.add_root', rRootBone, icon='FORWARD')


###---user pref pannel
class QuickRenamePrefPanel(bpy.types.AddonPreferences):
    bl_idname = __name__

    RN_renameData = bpy.props.BoolProperty(
        name="Rename Data",
        default=False,
        )

    RN_renameLinked = bpy.props.BoolProperty(
        name="Allow rename multi users Data",
        default=False,
        )

    def draw(self, context):
        layout = self.layout
        layout.label(
            text="Also change object data name if enabled (only if mesh name is available)")
        layout.label(
            text="Not active for direct rename (only when a proposition is selected)")
        layout.prop(self, "RN_renameData")
        if self.RN_renameData:
            layout.prop(self, "RN_renameLinked")


###---Keymapping and register

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
