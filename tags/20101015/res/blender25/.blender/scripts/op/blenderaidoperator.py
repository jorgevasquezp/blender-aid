import bpy
import webbrowser
import random
import http.client
import json

def check():
    connection=http.client.HTTPConnection("localhost:8080")
    connection.request("POST", "/service/productionview")
    connection.send("{}\r\n".encode())
    response=connection.getresponse()
    bdata=response.read()
    data=json.loads(bdata.decode())
    result = len(data[3])
    return result

class GoToBlenderAid(bpy.types.Operator):
    ''''''
    bl_idname = "aid.startblenderaid"
    bl_label = "Start blender-aid"
    missinglinks= bpy.props.IntProperty(name="Missing links", description="Number of missing links in this production", default=check())
    
    def poll(self, context):
        return True

    def execute(self, context):
        webbrowser.open("http://localhost:8080")
        return ('FINISHED',)

bpy.ops.add(GoToBlenderAid)

