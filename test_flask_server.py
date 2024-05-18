import unittest
from flask import Flask, request, Response, render_template_string
from flask_testing import TestCase
import threading
import cv2
import time
from queue import Queue
from app import app, frame_queue  # Assuming the main app is in app.py
import marshal

class TestFlaskServer(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.client = self.app.test_client()

    # def test_index_page(self):
    #     """Test that the index page loads correctly"""
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Video Stream', response.data)

    def test_stream_endpoint(self):


        def capture_frames(client):
            """Capture frames from the system webcam and put them in the queue"""
            cap = cv2.VideoCapture(0)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                _, buffer = cv2.imencode('.jpg', frame)
                # if frame_queue.full():
                #     frame_queue.get()  # Remove the oldest frame if the queue is full
                # frame_queue.put(buffer.tobytes())
                # response = client.post('/stream', data=buffer.tobytes())

                data=marshal.dumps({
                    "data": buffer.tobytes(),
                })

                # print(buffer.tobytes())
                response = self.client.post("/stream", data=data)
                # print(response)
            cap.release()

        # Start capturing frames from the webcam in a background thread
        threading.Thread(target=capture_frames, daemon=True, args=(self.client,)).start()
        time.sleep(9999)



        """Test that the /stream endpoint accepts frames"""
        # response = self.client.post('/stream', data={'data':b'bytes'})
        response = self.client.post("/stream", data={
            "name": "Flask",
            "theme": "dark",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Frame received')

    # def test_view_endpoint(self):
    #     """Test that the /view endpoint streams frames"""
    #     def add_test_frame():
    #         if frame_queue.full():
    #             frame_queue.get()  # Remove the oldest frame if the queue is full
    #         frame_queue.put(b'test frame')

    #     threading.Thread(target=add_test_frame, daemon=True).start()
    #
    #     response = self.client.get('/view')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(response.data.startswith(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'))

    # def test_frame_queue(self):
    #     """Test that frames are added to the queue"""
    #     frame = b'test frame'
    #     if frame_queue.full():
    #         frame_queue.get()  # Remove the oldest frame if the queue is full
    #     frame_queue.put(frame)
    #     self.assertFalse(frame_queue.empty())
    #     self.assertEqual(frame_queue.get(), frame)

if __name__ == '__main__':
    unittest.main()
