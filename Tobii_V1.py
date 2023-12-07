import g3pylib as g
import asyncio
import csv
import json
async def calibrate():
    try:
        async with g.connect_to_glasses.with_url("ws://192.168.75.51/websocket") as g3:
            await g3.calibrate.emit_markers()
            result = await g3.calibrate.run()
            return result
    except Exception as e:
        print(e)

async def Start_Streaming(gaze_queue, temp_writer):
    # async with g.connect_to_glasses.with_url("ws://192.168.75.51/websocket") as g3:
    #     gaze_queue, unsubscribe_to_gaze = await g3.rudimentary.subscribe_to_gaze()
    #     await g3.rudimentary.start_streams()
    # with open(filepath,"a",newline='') as tobii_file:
    #     temp_writer = csv.writer(tobii_file,delimiter=',')
    for i in range(50):
        gaze_sample = await gaze_queue.get() #empty the gaze_queue for await unsubscribe to work
        # q.put(gaze_sample)
        
        # new_dic = json.loads(gaze_sample[1])
        if len(gaze_sample)<=1:
            continue
        new_dic = gaze_sample[1]
        temp_list = new_dic["gaze2d"] if "gaze2d" in new_dic else [0,0]
        temp_list += new_dic["gaze3d"] if "gaze3d" in new_dic else [0,0,0]
        temp_list.append(new_dic["eyeleft"]["pupildiameter"] if ("eyeleft" in new_dic and "pupildiameter" in new_dic["eyeleft"]) else 0)
        temp_list.append(new_dic["eyeright"]["pupildiameter"] if ("eyeright" in new_dic and "pupildiameter" in new_dic["eyeright"]) else 0)
        temp_writer.writerow(temp_list)
        # await unsubscribe_to_gaze
            # print(gaze_sample)
            # exit(0)

# async def write_to_file(q,file_path):
