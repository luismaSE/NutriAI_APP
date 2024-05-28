import os
import requests #type: ignore
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

    # def draw_boxes(self,tmp_image, result):
    #     color = (0,0, 255)  # Color para las bounding boxes
    #     for item in result:
    #         class_name = item["name"]
    #         class_id = item["class"]
    #         conf = round(item["confidence"], 2)
    #         box = item["box"]
    #         x1, y1, x2, y2 = int(box["x1"]), int(box["y1"]), int(box["x2"]), int(box["y2"])

    #         # Dibujar la bounding box
    #         cv2.rectangle(tmp_image, (x1, y1), (x2, y2), color, 2)

    #         # Agregar etiqueta y confianza
    #         label = f'{class_name}: {conf}'
    #         # tomar escala de la imagen original para determinar el tamaño de la fuente
    #         text_scale=max(1, int(1 * tmp_image.shape[0] / 10)),
    #         cv2.putText(tmp_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, text_scale, color, 2)
    #         # cv2.putText(tmp_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    #     return tmp_image

    def draw_polygons(self, image_cv, result_json):
        try:
            result = result_json

            # Calcula un factor de escala basado en la altura de la imagen
            height = image_cv.shape[0]
            scale_factor = height / 400  # Ajusta el divisor para controlar la escala

            annotated_image = image_cv.copy()
            for i, item in enumerate(result):
                class_name = item.get("name")
                confidence = item.get("confidence")
                segments = item.get("segments")

                if segments:
                    mask = [(int(x), int(y)) for x, y in zip(segments.get("x", []), segments.get("y", []))]
                    if mask:
                        mask_array = np.array(mask)

                        # Escala el grosor de la línea
                        line_thickness = max(1, int(2 * scale_factor)) 
                        cv2.drawContours(annotated_image, [mask_array], -1, colors(i), line_thickness)

                        polygon = ShapelyPolygon(mask)
                        centroid = polygon.centroid
                        centroid_x = int(centroid.x)
                        centroid_y = int(centroid.y)

                        label = f"{class_name}: {confidence:.2f}"

                        # Escala el tamaño de la fuente
                        font_scale = max(0.2, scale_factor)
                        (text_width, text_height) = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, line_thickness)[0]

                        label_x = max(centroid_x - text_width // 2, 0)
                        label_y = max(centroid_y + text_height // 2, 0)
                        print('tamano img:',height)
                        print('escala:', scale_factor)
                        print('line_thickness:', line_thickness)
                        cv2.putText(annotated_image, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX,
                                    font_scale, colors(i), line_thickness)

            return annotated_image
        except Exception as e:
            print(f"Error al procesar los datos JSON: {e}")
            return None










    # def draw_polygons(self, image_cv, result_json):
    #     try:
    #         result = result_json
    #         annotator = Annotator(image_cv, line_width=2)

    #         for i,item in enumerate(result):
    #             class_name = item.get("name")
    #             confidence = item.get("confidence")
    #             segments = item.get("segments")
    #             if segments:
    #                 mask = [(int(x), int(y)) for x, y in zip(segments.get("x", []), segments.get("y", []))]
    #                 if mask:
    #                     annotator.seg_bbox(mask=mask,
    #                                         mask_color=colors(i, True),
    #                                         det_label=class_name)
    #             else:
    #                 raise Exception("No se encontraron segmentos en el resultado")
    #         annotated_image = annotator.result()
    #         return annotated_image
    #     except Exception as e:
    #         print(f"Error al procesar los datos JSON: {e}")
    #         return None







