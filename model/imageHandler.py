import os
import requests
from ultralytics.utils.plotting import Annotator, colors
import cv2
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon
import json

class ImageHandler:
    def __init__(self):
        pass


    def send_image(self, image , url):
        files = {'image': image}
        response = requests.post(url, files=files)
        return response

    def draw_boxes(self,tmp_image, result):
        color = (0,0, 255)  # Color para las bounding boxes
        for item in result:
            class_name = item["name"]
            class_id = item["class"]
            conf = round(item["confidence"], 2)
            box = item["box"]
            x1, y1, x2, y2 = int(box["x1"]), int(box["y1"]), int(box["x2"]), int(box["y2"])
            
            # Dibujar la bounding box
            cv2.rectangle(tmp_image, (x1, y1), (x2, y2), color, 2)
            
            # Agregar etiqueta y confianza
            label = f'{class_name}: {conf}'
            cv2.putText(tmp_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return tmp_image

    def draw_polygons(self, image_cv, result_json):
        try:
            result = result_json
            annotator = Annotator(image_cv, line_width=2)
            
            for item in result:
                class_name = item.get("name")
                confidence = item.get("confidence")
                segments = item.get("segments")
                if segments:
                    mask = [(int(x), int(y)) for x, y in zip(segments.get("x", []), segments.get("y", []))]
                    if mask:
                        annotator.seg_bbox(mask=mask,
                                            mask_color=colors(int(item.get("class")), True),
                                            det_label=class_name)
                else:
                    raise Exception("No se encontraron segmentos en el resultado")
            annotated_image = annotator.result()
            return annotated_image
        except Exception as e:
            print(f"Error al procesar los datos JSON: {e}")
            return None
    
    
    
    # def draw_polygons(self, image_cv, result_json):
    #     try:
    #         result = result_json
    #         annotator = Annotator(image_cv, line_width=2)
            
    #         for item in result:
    #             class_name = item.get("name")
    #             confidence = item.get("confidence")
    #             segments = item.get("segments")
    #             if segments:
    #                 mask = [(int(x), int(y)) for x, y in zip(segments.get("x", []), segments.get("y", []))]
    #                 if mask:
    #                     # Calcula el centro de la máscara
    #                     center_x = sum([p[0] for p in mask]) / len(mask)
    #                     center_y = sum([p[1] for p in mask]) / len(mask)

    #                     # Dibuja la máscara
    #                     annotator.seg_bbox(mask=mask,
    #                                         mask_color=colors(int(item.get("class")), True),
    #                                         det_label=None)  # No muestra la etiqueta aquí

    #                     # Muestra la etiqueta en el centro de la máscara
    #                     annotator.text((int(center_x), int(center_y)), text=f"{class_name}: {confidence}", color='white')

    #         annotated_image = annotator.result()
    #         return annotated_image
    #     except Exception as e:
    #         print(f"Error al procesar los datos JSON: {e}")
    #         return None



