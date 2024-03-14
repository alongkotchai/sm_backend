import os
import base64
from threading import Event
from queue import Queue
from typing import Callable
import cv2
import numpy as np
from ultralytics import YOLO

BASE_PATH: str = None


def get_img_data(fname: str):
    return fname.split(',')[1]


def readb64(uri):
    nparr = np.frombuffer(base64.b64decode(uri), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def get_swine_lenght(swine_number, swine_length_vote):
    swine_length = {0.0: 0, 1.0: 0}
    # insert swine length
    for cls in swine_length_vote[swine_number].keys():
        max_key, max_value = max(
            swine_length_vote[swine_number][cls].items(), key=lambda x: x[1])
        swine_length[cls] = max_key
    return swine_length


def predict(qin: Queue, qout: Queue, e: Event, ef: callable, tid: str):
    try:
        print(f'rt {tid} begin predict')
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        model_path = os.path.join(BASE_PATH, 'train_1_1_best.pt')
        tracker_path = os.path.join(BASE_PATH, 'bytetrack_cus.yaml')

        model = YOLO(model_path, verbose=False)

        swine_count = 0
        swine_pass_pointer = 0
        swine_pass_offset = 2
        swine_id = dict()
        swine_length_vote = dict()
        swine_image = dict()
        swine_axis = -10000
        frame_count = 0
        sampling_rate = 1
        # for capture image frame
        is_capture_valid = [False, False]
        is_captured = False

        # swine_outcome = {}

        # Loop through the video frames
        while True:

            try:
                data_in = qin.get(timeout=10)
                print(f'rt {tid} get new data {frame_count}')

            except Exception as e:
                print('get time out', e)
                raise e

            if data_in == 'q' or not e.is_set():
                print('quit command')
                break

            data = get_img_data(data_in)
            frame = readb64(data)

            print(f'rt {tid} image from base64')

            frame_count += 1

            if frame_count % sampling_rate != 0:
                continue

            # Run YOLOv8 tracking on the frame, persisting tracks between frames
            results = model.track(
                frame, persist=True,
                tracker=tracker_path,
                agnostic_nms=True,
                verbose=False)

            annotated_frame = results[0].plot()

            if not results[0].boxes.is_track:
                try:
                    print(f'put 0 f {frame_count}')
                    qout.put({
                        'frame': True,
                        'length': {},
                        'image': annotated_frame
                    }, timeout=10)
                except Exception as e:
                    print('error put0', e)
                    break
                finally:
                    continue

            id_list = results[0].boxes.id.tolist()

            for i in range(len(id_list)):
                bbox = results[0].boxes.xywh.tolist()[i]  # in format XYWH
                id_x_center = bbox[0]
                # assume 1 cm = 13 px => 0.077 cm = 1 px and round it to *.0/*.5
                id_width = round((bbox[2] * 0.077)*2)/2
                id_class = results[0].boxes.cls.tolist()[i]

                if id_x_center > 100 and id_x_center < 1165:  # 1165 = image_width*60%
                    if id_x_center - swine_axis > 600:
                        # set ID and increase swine number
                        swine_count += 1
                        swine_image[swine_count] = np.array([])
                        swine_id[swine_count] = set()
                        swine_axis = id_x_center
                        swine_id[swine_count].add(id_list[i])
                        swine_length_vote[swine_count] = {
                            0.0: {0.0: 0, 0.5: 0, 1.0: 0, 1.5: 0, 2.0: 0, 2.5: 0, 3.0: 0, 3.5: 0, 4.0: 0, 4.5: 0, 5.0: 0, 5.5: 0, 6.0: 0, 6.5: 0, 7.0: 0},
                            1.0: {0.0: 0, 0.5: 0, 1.0: 0, 1.5: 0, 2.0: 0, 2.5: 0, 3.0: 0, 3.5: 0, 4.0: 0, 4.5: 0, 5.0: 0, 5.5: 0, 6.0: 0, 6.5: 0, 7.0: 0}}
                        is_captured = False
                        is_capture_valid = [False, False]
                        # vote width
                        swine_length_vote[swine_count][id_class][id_width] += 1

                        # get swine length vote outcome from the swine_count - offset
                        swine_pass_pointer = swine_count - swine_pass_offset
                        if swine_pass_pointer > 0:
                            length = get_swine_lenght(
                                swine_pass_pointer, swine_length_vote)
                            # swine_outcome[swine_pass_pointer] = {
                            #     'length': length,
                            #     'image': swine_image[swine_pass_pointer]
                            # }
                            try:
                                print(f'put 1 f {frame_count}')
                                qout.put({
                                    'frame': False,
                                    'swime_number': swine_pass_pointer,
                                    'length': length,
                                    'image': swine_image[swine_pass_pointer]
                                }, timeout=10)
                            except Exception as e:
                                print('error put1', e)
                                break
                    elif id_x_center - swine_axis < -600:
                        # ID from previous swine
                        swine_id[swine_count-1].add(id_list[i])
                        # vote width
                        swine_length_vote[swine_count -
                                          1][id_class][id_width] += 1

                    else:
                        # ID from the same swine
                        swine_id[swine_count].add(id_list[i])
                        swine_axis = id_x_center
                        # vote width
                        swine_length_vote[swine_count][id_class][id_width] += 1
                        if swine_length_vote[swine_count][id_class][id_width] > 20:
                            is_capture_valid[int(id_class)] = True

                # print(is_capture_valid)
                if is_capture_valid[0] and is_capture_valid[1] and not is_captured:
                    # print('capture')
                    swine_image[swine_count] = annotated_frame
                    is_captured = True

                try:
                    print(f'put 2 f {frame_count}')
                    qout.put({
                        'frame': True,
                        'length': {},
                        'image': annotated_frame
                    }, timeout=10)
                except Exception as e:
                    print('error put2', type(e))
                    break

        # get length of all last offset swine
        print('try take data beyond offset')
        for i in range(max(swine_pass_pointer+1, 1), swine_count+1):
            length = get_swine_lenght(
                i, swine_length_vote)
            # swine_outcome[i] = {
            #     'length': length,
            #     'image': swine_image[i]
            # }
            try:
                print(f'put 3 f {frame_count}')

                qout.put({
                    'frame': False,
                    'swime_number': i,
                    'length': length,
                    'image': swine_image[i]
                }, timeout=10)
            except Exception as e:
                print('error put3', e)
                break

    except Exception as e:
        print('error', e)
        qout.put_nowait('f')
        raise e

    finally:
        print('finally')
        ef(tid)
        qout.put_nowait('q')
