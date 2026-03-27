import time
import grpc
import cv2
import numpy as np

from infra.grpc.protos import model_pb2 as pb2
from infra.grpc.protos import model_pb2_grpc as pb2_grpc


class InferenceConnection:
    def __init__(
        self,
        target: str,
        confidence: float = 0.10,
        timeout_sec: float = 10.0,
        jpeg_quality: int = 90,
        max_msg: int = 64 * 1024 * 1024,
    ):
        self.confidence = float(confidence)
        self.timeout_sec = float(timeout_sec)
        self.jpeg_quality = int(jpeg_quality)

        self.channel = grpc.insecure_channel(
            target,
            options=[
                ("grpc.max_send_message_length", max_msg),
                ("grpc.max_receive_message_length", max_msg),
            ],
        )
        self.stub = pb2_grpc.ModelMethodsStub(self.channel)

    def _ndarray_to_jpg_bytes(self, img: np.ndarray) -> bytes:
        if img is None:
            raise ValueError("img é None")
        ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
        if not ok:
            raise RuntimeError("Falha ao codificar JPEG")
        return buf.tobytes()

    def _parse_proto_like(self, resp, decode_segmentation: bool = True):
        # list_bbox (repeated BBox)
        list_bbox = [{
            "x": float(b.x),
            "y": float(b.y),
            "w": float(b.w),
            "h": float(b.h),
            "label": str(b.label),
            "class_id": int(b.class_id),
            "confidence": float(b.confidence),
        } for b in resp.list_bbox]

        # defect_list (repeated DefectInfo)
        class_list = [{
            "name": str(c.name),
            "class_id": int(c.class_id),
            "ui_color": {"r": int(c.ui_color.r), "g": int(c.ui_color.g), "b": int(c.ui_color.b)},
            "mask_color": {"r": int(c.mask_color.r), "g": int(c.mask_color.g), "b": int(c.mask_color.b)},
        } for c in resp.class_list]

        # img_segmentation (bytes) + opcional np.ndarray
        raw = resp.img_segmentation or b""
        seg_img = None
        if decode_segmentation and raw:
            nparr = np.frombuffer(raw, np.uint8)
            # Padrao: PNG colorido (RGB)
            seg_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        return {
            "model_name": str(resp.model_name),
            "list_bbox": list_bbox,
            #"img_segmentation": raw,          # igual ao proto (bytes)
            "img_segmentation_image": seg_img, # extra opcional (pode remover se quiser 100% proto)
            "class_list": class_list,
            "error": str(resp.error),
        }

    def infer_bytes(self, image_bytes: bytes, decode_segmentation: bool = True):
        t0 = time.perf_counter()
        resp = self.stub.infer(
            pb2.InferRequest(
                image_bytes=image_bytes,
                confidence_threshold=self.confidence,
            ),
            timeout=self.timeout_sec,
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0

        out = self._parse_proto_like(resp, decode_segmentation=decode_segmentation)
        out["latency_ms"] = latency_ms  # se não quiser, apaga esta linha
        return out

    def infer_ndarray(self, img: np.ndarray, decode_segmentation: bool = True):
        return self.infer_bytes(self._ndarray_to_jpg_bytes(img), decode_segmentation=decode_segmentation)

    def infer_future_bytes(self, image_bytes: bytes):
        return self.stub.infer.future(
            pb2.InferRequest(image_bytes=image_bytes, confidence_threshold=self.confidence),
            timeout=self.timeout_sec,
        )

    def infer_future_ndarray(self, img: np.ndarray):
        return self.infer_future_bytes(self._ndarray_to_jpg_bytes(img))
