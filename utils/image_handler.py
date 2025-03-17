import colorsys
import requests
import cv2
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon

class ImageHandler:
    def send_image(self, image, url):
        files = {'image': image}
        response = requests.post(url, files=files)
        return response

    # def draw_polygons(self, image_cv, result_json):
    #     try:
    #         result = result_json
    #         height = image_cv.shape[0]
    #         scale_factor = height / 400
    #         annotated_image = image_cv.copy()
    #         for i, item in enumerate(result):
    #             class_name = item.get("name")
    #             confidence = item.get("confidence")
    #             segments = item.get("segments")
    #             if segments:
    #                 mask = [(int(x), int(y)) for x, y in zip(segments.get("x", []), segments.get("y", []))]
    #                 if mask:
    #                     mask_array = np.array(mask)
    #                     line_thickness = max(1, int(2 * scale_factor))
    #                     cv2.drawContours(annotated_image, [mask_array], -1, (0, 255, 0), line_thickness)
    #                     polygon = ShapelyPolygon(mask)
    #                     centroid = polygon.centroid
    #                     centroid_x = int(centroid.x)
    #                     centroid_y = int(centroid.y)
    #                     label = f"{class_name}: {confidence:.2f}"
    #                     font_scale = max(0.2, scale_factor)
    #                     (text_width, text_height) = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, line_thickness)[0]
    #                     label_x = max(centroid_x - text_width // 2, 0)
    #                     label_y = max(centroid_y + text_height // 2, 0)
    #                     # cv2.putText(annotated_image, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), line_thickness)
    #         return annotated_image
    #     except Exception as e:
    #         print(f"Error al procesar los datos JSON: {e}")
    #         return None
    
    
    def draw_polygons(self, image_cv, result_json):
        try:
            result = result_json
            height = image_cv.shape[0]
            scale_factor = height / 400
            annotated_image = image_cv.copy()
            
            # Diccionario para asignar colores consistentes a cada clase
            class_color_map = {}
            color_counter = 0
            
            for i, item in enumerate(result):
                class_name = item.get("name")
                confidence = item.get("confidence")
                segments = item.get("segments")
                if segments:
                    mask = [(int(x), int(y)) for x, y in zip(segments.get("x", []), segments.get("y", []))]
                    if mask:
                        mask_array = np.array(mask)
                        
                        # Asignar un color si la clase no tiene uno aún
                        if class_name not in class_color_map:
                            # Generar color en el espacio HSV para mayor variedad
                            hue = (color_counter * 137.5) % 360  # Incremento para dispersión óptima
                            saturation = 1.0
                            value = 1.0
                            rgb = colorsys.hsv_to_rgb(hue / 360, saturation, value)
                            color = tuple(int(c * 255) for c in rgb)
                            class_color_map[class_name] = color
                            color_counter += 1
                        else:
                            # Reutilizar el color ya asignado a la clase
                            color = class_color_map[class_name]
                        
                        # Ajustar grosor de línea según la escala
                        line_thickness = max(1, int(2 * scale_factor))
                        cv2.drawContours(annotated_image, [mask_array], -1, color, line_thickness)
                        
                        # Dibujar máscara transparente
                        overlay = annotated_image.copy()
                        cv2.fillPoly(overlay, [mask_array], color)
                        alpha = 0.3  # Nivel de transparencia
                        cv2.addWeighted(overlay, alpha, annotated_image, 1 - alpha, 0, annotated_image)
            
            return annotated_image
        except Exception as e:
            print(f"Error al procesar los datos JSON: {e}")
            return None