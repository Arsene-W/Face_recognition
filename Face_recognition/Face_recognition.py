import numpy as np
from openvino.inference_engine import IENetwork, IEPlugin
import sys
import cv2
import time
import os


def load_detection_model():
    global plugin
    global detection_net
    plugin = IEPlugin(device="MYRIAD")
    #########################################################################

    #########################  Load Neural Network  #########################
    #  Read in Graph file (IR)
    detection_net = IENetwork.from_ir(model="face-detection-adas-0001.xml", weights="face-detection-adas-0001.bin")

    global detection_input_blob
    global detection_out_blob
    detection_input_blob = next(iter(detection_net.inputs))
    detection_out_blob = next(iter(detection_net.outputs))
    #  Load network to the plugin
    global detection_exec_net
    #help(IEPlugin.load)
    detection_exec_net = plugin.load(network=detection_net,num_requests=1)
    del detection_net


def load_recognition_model():
    #######################  Device  Initialization  ########################
    #  Plugin initialization for specified device and load extensions library if specified

    global  recognition_net

    #########################################################################

    #########################  Load Neural Network  #########################
    #  Read in Graph file (IR)
    recognition_net = IENetwork.from_ir(model="face-reidentification-retail-0095.xml", weights="face-reidentification-retail-0095.bin")

    global  input_blob
    global  out_blob
    input_blob = next(iter(recognition_net.inputs))
    out_blob = next(iter(recognition_net.outputs))
    #  Load network to the plugin
    global  exec_net
    exec_net = plugin.load(network=recognition_net,num_requests=1)
    del recognition_net
    ########################################################################


def get_bounding(image_file):

    frame = cv2.imread(image_file)

    # Prepare input blob and perform an inference
    blob = cv2.dnn.blobFromImage(frame, size=(672, 384), ddepth=cv2.CV_8U)
    ########################################################################

    ##########################  Start  Inference  ##########################
    #  Start synchronous inference and get inference result
    req_handle = detection_exec_net.start_async(request_id=0, inputs={detection_input_blob: blob})
    ########################################################################

    ######################## Get Inference Result  #########################
    status = req_handle.wait()
    out = req_handle.outputs[detection_out_blob]
    # print(res)




    # name = os.path.splitext(os.path.basename(image_file))[0]
    # frame = cv2.imread(image_file)
    #
    # # Prepare input blob and perform an inference
    # blob = cv2.dnn.blobFromImage(frame, size=(672, 384), ddepth=cv2.CV_8U)
    # detection_net.setInput(blob)
    # out = detection_net.forward()

    # Draw detected faces on the frame
    name = os.path.splitext(os.path.basename(image_file))[0]

    for detection in out.reshape(-1, 7):
        confidence = float(detection[2])
        xmin = int(detection[3] * frame.shape[1])
        ymin = int(detection[4] * frame.shape[0])
        xmax = int(detection[5] * frame.shape[1])
        ymax = int(detection[6] * frame.shape[0])

        if ymin<0:
            ymin=0
        if xmin<0:
            xmin=0
        if confidence > 0.5:
            img = frame[ymin:ymax, xmin:xmax]
            cv2.imwrite('./images/'+name+'_face.jpg', img)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color=(0, 255, 0))

            return img



    # Save the frame to an image file
    #cv2.imwrite('out.png', frame)


def get_feature(image):
    #########################  Obtain Input Tensor  ########################
    #  Obtain and preprocess input tensor (image)
    #  Read and pre-process input image  maybe we don't need to show these details


    #  Preprocessing is neural network dependent maybe we don't show this
    # n, c, h, w = net.inputs[input_blob]
    image = cv2.resize(image, (128, 128))
    image = image.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    image = image.reshape((1, 3, 128, 128))
    ########################################################################

    ##########################  Start  Inference  ##########################
    #  Start synchronous inference and get inference result
    req_handle = exec_net.start_async(request_id=0,inputs={input_blob: image})
    ########################################################################

    ######################## Get Inference Result  #########################
    status = req_handle.wait()
    res = req_handle.outputs[out_blob]

    res=res.reshape(-1)


    return res
    # Do something with the results... (like print top 5)
    # print(type(out_blob))
    # out_blob=0
    # top_ind = np.argsort(res[out_blob], axis=1)[0, -5:][::-1]
    # for i in top_ind:
    #     print("%f #%d" % (res[out_blob][0, i], i))

    ###############################  Clean  Up  ############################
    # del exec_net
    # del plugin
    ########################################################################



def recognition(per1,per2):
    dis = 1 - np.dot(per1, per2) / (np.linalg.norm(per1) * np.linalg.norm(per2))
    print('Distance:',dis)
    if dis<0.5:
        return 1
    else:
        return 0


def register(image_file):
    name = os.path.splitext(os.path.basename(image_file))[0]
    face=get_bounding(image_file)
    if face is None:
        print('No face!')
        return 0
    feature = get_feature(face)
    np.savetxt('./images/' + name.rstrip('_new') + '.txt', feature)
    os.rename('./images/' + name + '.jpg', './images/' + name.rstrip('_new') + '.jpg')
    os.rename('./images/' + name + '_face.jpg', './images/' + name.rstrip('_new') + '_face.jpg')
    return 1

def FaceAPI(image_file):
    print('image:')
    print(image_file)
    name = os.path.splitext(os.path.basename(image_file))[0]
    try:
        feature=np.loadtxt('./images/' + name.rstrip('_new') + '.txt')
        print('./images/' + name.rstrip('_new') + '.txt')
    except:
        flag=register(image_file)
        if flag==0:
            print('Register failure,no face!')
            return 0
        print('Register susscss!')
        return 1

    face=get_bounding(image_file)
    if face is None:
        print('No face!')
        return 0

    per1=get_feature(face)

    result= recognition(per1,feature)

    return result




if __name__ == '__main__':
    load_detection_model()
    load_recognition_model()
    time_start = time.time()

    face1=get_bounding("./images/2588373621_new.jpg")
    face2=get_bounding("./images/0598497760_new.jpg")
    if face1 is None:
        print('None1')
        exit(1)
    if face2 is None:
        print('None2')
        exit(1)

    per1=get_feature(face1)
    #per1=per1.reshape(-1)

    per2=get_feature(face2)
    #per2=per2.reshape(-1)

    dis=1 - np.dot(per1,per2)/(np.linalg.norm(per1)*np.linalg.norm(per2))
    time_end = time.time()
    print('************************************************************')
    print('time:',time_end-time_start)
    print(dis)

    # load_model()
    # FaceAPI("./images/2588834773_new.jpg")
    #
    # del net
    # del exec_net
    # del plugin
