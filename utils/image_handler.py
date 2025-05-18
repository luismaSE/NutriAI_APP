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

    def _rect_intersects(self, rect1, rect2):
        """Verifica si dos rectángulos se intersectan."""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def draw_polygons(self, image_cv, result_json):
        try:
            result = result_json
            height = image_cv.shape[0]
            scale_factor = height / 400  # Escalar según la altura de la imagen
            annotated_image = image_cv.copy()
            
            # Diccionario para asignar colores consistentes a cada clase
            class_color_map = {}
            color_counter = 0
            label_positions = []  # Lista de rectángulos ocupados por etiquetas

            for i, item in enumerate(result):
                class_name = item.get("name")
                if class_name.lower() == 'unknown':
                    continue  # Saltar elementos desconocidos
                confidence = item.get("confidence")
                segments = item.get("segments")
                if segments:
                    mask = [(int(x), int(y)) for x, y in zip(segments.get("x", []), segments.get("y", []))]
                    if mask:
                        mask_array = np.array(mask, dtype=np.int32)
                        if len(mask_array) < 3:
                            continue  # Saltar máscaras con menos de 3 puntos
                        
                        # Asignar color consistente por clase
                        if class_name not in class_color_map:
                            hue = (color_counter * 137.5) % 360  # Dispersión de colores
                            saturation = 1.0
                            value = 1.0
                            rgb = colorsys.hsv_to_rgb(hue / 360, saturation, value)
                            color = tuple(int(c * 255) for c in rgb)
                            class_color_map[class_name] = color
                            color_counter += 1
                        else:
                            color = class_color_map[class_name]
                        
                        # Dibujar contorno de la máscara
                        line_thickness = max(1, int(2 * scale_factor))
                        cv2.drawContours(annotated_image, [mask_array], -1, color, line_thickness)
                        
                        # Dibujar máscara transparente
                        overlay = annotated_image.copy()
                        cv2.fillPoly(overlay, [mask_array], color)
                        alpha = 0.3  # Transparencia
                        cv2.addWeighted(overlay, alpha, annotated_image, 1 - alpha, 0, annotated_image)
                        
                        # Calcular posición del texto (centroide)
                        M = cv2.moments(mask_array)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                        else:
                            cX, cY = mask_array[0]
                        
                        # Ajustar posición del texto para evitar superposiciones
                        text_size, _ = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5 * scale_factor, 2)
                        text_width, text_height = text_size
                        label_rect = (cX, cY - text_height, text_width, text_height)
                        
                        # Verificar superposición y ajustar posición
                        while any(self._rect_intersects(label_rect, pos) for pos in label_positions):
                            cY -= text_height  # Mover hacia arriba
                            label_rect = (cX, cY - text_height, text_width, text_height)
                        
                        # Asegurarse de que el texto no se salga de la imagen
                        if cX + text_width > annotated_image.shape[1]:
                            cX = annotated_image.shape[1] - text_width
                        if cY - text_height < 0:
                            cY = text_height
                        
                        # Dibujar texto con contorno negro
                        cv2.putText(
                            annotated_image, 
                            class_name, 
                            (cX, cY), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5 * scale_factor, 
                            (0, 0, 0),  # Contorno negro
                            3,  # Grosor del contorno
                            cv2.LINE_AA
                        )
                        # Dibujar texto con el mismo color que la máscara
                        cv2.putText(
                            annotated_image, 
                            class_name, 
                            (cX, cY), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5 * scale_factor, 
                            color,  # Color de la máscara
                            2,  # Grosor del texto
                            cv2.LINE_AA
                        )
                        
                        # Agregar posición a la lista de etiquetas dibujadas
                        label_positions.append(label_rect)
            
            return annotated_image
        except Exception as e:
            print(f"Error al procesar los datos JSON: {e}")
            return None