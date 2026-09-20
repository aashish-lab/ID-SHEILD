import os
import cv2
import numpy as np

def generate_test_samples(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    def draw_face_portrait(img, x, y, size, hair_color=(40, 30, 20), skin_color=(210, 180, 160)):
        # Head oval
        cv2.ellipse(img, (x + size//2, y + size//2), (size//3, size//2), 0, 0, 360, skin_color, -1)
        # Hair
        cv2.ellipse(img, (x + size//2, y + size//4), (size//3 + 2, size//4), 0, 180, 360, hair_color, -1)
        # Eyes
        eye_y = y + int(size * 0.45)
        cv2.circle(img, (x + int(size * 0.35), eye_y), int(size * 0.07), (255, 255, 255), -1)
        cv2.circle(img, (x + int(size * 0.65), eye_y), int(size * 0.07), (255, 255, 255), -1)
        cv2.circle(img, (x + int(size * 0.35), eye_y), int(size * 0.035), (30, 30, 30), -1)
        cv2.circle(img, (x + int(size * 0.65), eye_y), int(size * 0.035), (30, 30, 30), -1)
        # Eyebrows
        cv2.line(img, (x + int(size * 0.28), eye_y - 8), (x + int(size * 0.42), eye_y - 9), hair_color, 2)
        cv2.line(img, (x + int(size * 0.58), eye_y - 9), (x + int(size * 0.72), eye_y - 8), hair_color, 2)
        # Nose
        cv2.line(img, (x + size//2, eye_y), (x + size//2, y + int(size * 0.65)), (180, 140, 120), 2)
        # Mouth
        cv2.ellipse(img, (x + size//2, y + int(size * 0.78)), (int(size * 0.14), int(size * 0.06)), 0, 0, 180, (140, 60, 60), 2)

    # -------------------------------------------------------------
    # DEMO CASE 1: GENUINE IDENTITY
    # -------------------------------------------------------------
    case1_doc = np.ones((400, 640, 3), dtype=np.uint8) * 245
    cv2.rectangle(case1_doc, (0, 0), (640, 70), (45, 85, 140), -1)
    cv2.putText(case1_doc, "CITIZEN IDENTITY CARD - NATIONAL REGISTRY", (30, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    # Photo frame & portrait
    cv2.rectangle(case1_doc, (40, 100), (200, 300), (210, 210, 210), -1)
    cv2.rectangle(case1_doc, (40, 100), (200, 300), (100, 100, 100), 2)
    draw_face_portrait(case1_doc, 50, 110, 140)
    # Info text
    cv2.putText(case1_doc, "NAME: CITIZEN HOLDER", (225, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 2)
    cv2.putText(case1_doc, "DOCUMENT NO: ID-90214812", (225, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 2)
    cv2.putText(case1_doc, "DOB: 18 JUN 1992", (225, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
    cv2.putText(case1_doc, "EXPIRY: 31 DEC 2030", (225, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
    cv2.putText(case1_doc, "STATUS: CITIZEN / FULL RIGHTS", (225, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 120, 20), 2)
    cv2.imwrite(os.path.join(output_dir, "case1_doc.jpg"), case1_doc)

    case1_selfie = np.ones((300, 300, 3), dtype=np.uint8) * 235
    draw_face_portrait(case1_selfie, 60, 40, 180)
    cv2.imwrite(os.path.join(output_dir, "case1_selfie.jpg"), case1_selfie)

    # -------------------------------------------------------------
    # DEMO CASE 2: TAMPERED DOCUMENT
    # -------------------------------------------------------------
    case2_doc = case1_doc.copy()
    cv2.rectangle(case2_doc, (220, 150), (590, 190), (255, 255, 190), -1)
    cv2.rectangle(case2_doc, (220, 150), (590, 190), (0, 0, 220), 2)
    cv2.putText(case2_doc, "DOCUMENT NO: ID-99482-INVALID", (225, 178), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 180), 2)
    
    cv2.rectangle(case2_doc, (220, 110), (560, 145), (255, 240, 240), -1)
    cv2.putText(case2_doc, "NAME: ALTERED / FORGED USER", (225, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 0, 0), 2)
    
    noise = np.random.randint(0, 160, (90, 110, 3), dtype=np.uint8)
    case2_doc[280:370, 480:590] = cv2.addWeighted(case2_doc[280:370, 480:590], 0.3, noise, 0.7, 0)
    cv2.imwrite(os.path.join(output_dir, "case2_doc.jpg"), case2_doc)

    # -------------------------------------------------------------
    # DEMO CASE 3: IDENTITY MISMATCH
    # -------------------------------------------------------------
    case3_doc = np.ones((400, 640, 3), dtype=np.uint8) * 245
    cv2.rectangle(case3_doc, (0, 0), (640, 70), (35, 75, 110), -1)
    cv2.putText(case3_doc, "STATE DRIVER LICENSE - DEPARTMENT OF TRANSPORT", (30, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    cv2.rectangle(case3_doc, (40, 100), (200, 300), (210, 210, 210), -1)
    cv2.rectangle(case3_doc, (40, 100), (200, 300), (100, 100, 100), 2)
    draw_face_portrait(case3_doc, 50, 110, 140, hair_color=(20, 20, 20), skin_color=(210, 175, 150))
    cv2.putText(case3_doc, "NAME: VERIFIED CITIZEN", (225, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 2)
    cv2.putText(case3_doc, "LICENSE NO: DL-88219044", (225, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 2)
    cv2.putText(case3_doc, "DOB: 12 APR 1991", (225, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
    cv2.putText(case3_doc, "CLASS: C - OPERATOR", (225, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
    cv2.imwrite(os.path.join(output_dir, "case3_doc.jpg"), case3_doc)

    case3_selfie = np.ones((300, 300, 3), dtype=np.uint8) * 230
    draw_face_portrait(case3_selfie, 60, 40, 180, hair_color=(140, 80, 40), skin_color=(235, 195, 175))
    cv2.imwrite(os.path.join(output_dir, "case3_selfie.jpg"), case3_selfie)

    # -------------------------------------------------------------
    # BORDER CHECKPOINT SCENARIO A: GENUINE TRAVEL PASSPORT WITH MRZ
    # -------------------------------------------------------------
    pass_doc = np.ones((450, 680, 3), dtype=np.uint8) * 242
    # Passport header
    cv2.rectangle(pass_doc, (0, 0), (680, 65), (20, 45, 90), -1)
    cv2.putText(pass_doc, "PASSPORT - REPUBLIC IMMIGRATION & BORDER", (25, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (255, 255, 255), 2)
    # Photo
    cv2.rectangle(pass_doc, (35, 85), (205, 305), (215, 215, 215), -1)
    cv2.rectangle(pass_doc, (35, 85), (205, 305), (70, 70, 70), 2)
    draw_face_portrait(pass_doc, 45, 95, 150)
    # Bio details
    cv2.putText(pass_doc, "TYPE: P   CODE: UTO   PASSPORT NO: P98421074", (225, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(pass_doc, "SURNAME: CHEN   GIVEN NAMES: ALEXANDER", (225, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(pass_doc, "NATIONALITY: UTOPIAN   SEX: M", (225, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(pass_doc, "DATE OF BIRTH: 14 AUG 1994", (225, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(pass_doc, "EXPIRY DATE: 13 AUG 2031", (225, 255), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(pass_doc, "AUTHORITY: DEPT OF STATE", (225, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    # Consular Visa Stamp
    cv2.circle(pass_doc, (590, 200), 55, (40, 130, 40), 2)
    cv2.putText(pass_doc, "ENTRY VALID", (550, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (40, 130, 40), 1)
    cv2.putText(pass_doc, "IMMIGRATION", (548, 212), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (40, 130, 40), 1)
    # MRZ Machine Readable Zone
    cv2.rectangle(pass_doc, (0, 345), (680, 450), (230, 230, 230), -1)
    cv2.line(pass_doc, (0, 345), (680, 345), (140, 140, 140), 1)
    cv2.putText(pass_doc, "P<UTOCHEN<<ALEXANDER<<<<<<<<<<<<<<<<<<<<<<<<<", (20, 385), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.putText(pass_doc, "P984210744UTO9408144M3108138<<<<<<<<<<<<<<06", (20, 422), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2)
    cv2.imwrite(os.path.join(output_dir, "case_border_passport.jpg"), pass_doc)

    # Matching traveler live photo
    border_selfie = np.ones((320, 320, 3), dtype=np.uint8) * 238
    draw_face_portrait(border_selfie, 60, 45, 190)
    cv2.imwrite(os.path.join(output_dir, "case_border_passport_selfie.jpg"), border_selfie)

    # -------------------------------------------------------------
    # BORDER CHECKPOINT SCENARIO B: TAMPERED VISA STAMP & MODIFIED DOB
    # -------------------------------------------------------------
    tampered_visa = pass_doc.copy()
    # Tampered DOB field
    cv2.rectangle(tampered_visa, (220, 202), (520, 235), (255, 255, 180), -1)
    cv2.rectangle(tampered_visa, (220, 202), (520, 235), (0, 0, 220), 2)
    cv2.putText(tampered_visa, "DATE OF BIRTH: 22 MAR 1988 [MODIFIED]", (225, 222), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 180), 2)
    # Distorted / Tampered Visa Stamp
    cv2.circle(tampered_visa, (590, 200), 55, (0, 0, 230), 3)
    cv2.line(tampered_visa, (540, 170), (640, 230), (0, 0, 230), 2)
    cv2.putText(tampered_visa, "STAMP ALTERED", (542, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 230), 1)
    cv2.imwrite(os.path.join(output_dir, "case_border_tampered_visa.jpg"), tampered_visa)

    # -------------------------------------------------------------
    # BORDER CHECKPOINT SCENARIO C: BLACKLISTED / STOLEN TRAVEL CREDENTIAL
    # -------------------------------------------------------------
    bl_doc = pass_doc.copy()
    cv2.rectangle(bl_doc, (220, 95), (660, 130), (255, 230, 230), -1)
    cv2.putText(bl_doc, "TYPE: P   CODE: UTO   PASSPORT NO: P-BLOCKED-902", (225, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (180, 0, 0), 2)
    cv2.imwrite(os.path.join(output_dir, "case_border_blacklist.jpg"), bl_doc)

    print("All standard & Border Checkpoint test samples generated in:", output_dir)

if __name__ == "__main__":
    generate_test_samples(r"C:\Users\P Rahul\.gemini\antigravity\scratch\id-shield\static\uploads")
