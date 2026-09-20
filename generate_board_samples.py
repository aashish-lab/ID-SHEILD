import os
import cv2
import numpy as np

def create_board_samples(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    
    def draw_portrait(img, x, y, size, hair_color=(40, 30, 20), skin_color=(210, 180, 160), glasses=False, beard=False):
        # Head oval
        cv2.ellipse(img, (x + size//2, y + size//2), (size//3, size//2), 0, 0, 360, skin_color, -1)
        # Hair
        cv2.ellipse(img, (x + size//2, y + size//4), (size//3 + 4, size//4), 0, 180, 360, hair_color, -1)
        # Eyes
        eye_y = y + int(size * 0.45)
        cv2.circle(img, (x + int(size * 0.35), eye_y), int(size * 0.07), (255, 255, 255), -1)
        cv2.circle(img, (x + int(size * 0.65), eye_y), int(size * 0.07), (255, 255, 255), -1)
        cv2.circle(img, (x + int(size * 0.35), eye_y), int(size * 0.035), (30, 30, 30), -1)
        cv2.circle(img, (x + int(size * 0.65), eye_y), int(size * 0.035), (30, 30, 30), -1)
        # Eyebrows
        cv2.line(img, (x + int(size * 0.28), eye_y - 8), (x + int(size * 0.42), eye_y - 9), hair_color, 2)
        cv2.line(img, (x + int(size * 0.58), eye_y - 9), (x + int(size * 0.72), eye_y - 8), hair_color, 2)
        # Glasses (optional)
        if glasses:
            cv2.circle(img, (x + int(size * 0.35), eye_y), int(size * 0.11), (50, 50, 50), 2)
            cv2.circle(img, (x + int(size * 0.65), eye_y), int(size * 0.11), (50, 50, 50), 2)
            cv2.line(img, (x + int(size * 0.46), eye_y), (x + int(size * 0.54), eye_y), (50, 50, 50), 2)
        # Nose
        cv2.line(img, (x + size//2, eye_y), (x + size//2, y + int(size * 0.65)), (180, 140, 120), 2)
        # Mouth
        cv2.ellipse(img, (x + size//2, y + int(size * 0.78)), (int(size * 0.14), int(size * 0.06)), 0, 0, 180, (140, 60, 60), 2)
        # Beard (optional)
        if beard:
            cv2.ellipse(img, (x + size//2, y + int(size * 0.82)), (int(size * 0.22), int(size * 0.14)), 0, 0, 180, hair_color, -1)

    # =========================================================================
    # SAMPLE 1: GENUINE TRAVEL PASSPORT WITH MRZ
    # =========================================================================
    p1 = np.ones((460, 700, 3), dtype=np.uint8) * 244
    cv2.rectangle(p1, (0, 0), (700, 68), (18, 42, 85), -1)
    cv2.putText(p1, "PASSPORT - REPUBLIC IMMIGRATION & BORDER", (25, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), 2)
    # Photo frame & Portrait
    cv2.rectangle(p1, (35, 88), (210, 315), (215, 215, 215), -1)
    cv2.rectangle(p1, (35, 88), (210, 315), (60, 60, 60), 2)
    draw_portrait(p1, 45, 100, 155, hair_color=(30, 25, 20), skin_color=(215, 185, 165))
    # Bio Details
    cv2.putText(p1, "TYPE: P   CODE: UTO   PASSPORT NO: P98421074", (230, 118), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(p1, "SURNAME: CHEN   GIVEN NAMES: ALEXANDER", (230, 154), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(p1, "NATIONALITY: UTOPIAN   SEX: M", (230, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(p1, "DATE OF BIRTH: 14 AUG 1994", (230, 226), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(p1, "EXPIRY DATE: 13 AUG 2031", (230, 262), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    cv2.putText(p1, "AUTHORITY: DEPARTMENT OF STATE", (230, 298), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 20, 20), 2)
    # Authentic Consular Visa Stamp
    cv2.circle(p1, (605, 205), 58, (35, 130, 35), 2)
    cv2.putText(p1, "CONSULAR VISA", (555, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (35, 130, 35), 1)
    cv2.putText(p1, "ENTRY VALID", (560, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (35, 130, 35), 1)
    # ICAO 9303 MRZ Machine Readable Zone
    cv2.rectangle(p1, (0, 355), (700, 460), (232, 232, 232), -1)
    cv2.line(p1, (0, 355), (700, 355), (150, 150, 150), 1)
    cv2.putText(p1, "P<UTOCHEN<<ALEXANDER<<<<<<<<<<<<<<<<<<<<<<<<<", (20, 395), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (20, 20, 20), 2)
    cv2.putText(p1, "P984210744UTO9408144M3108138<<<<<<<<<<<<<<06", (20, 435), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (20, 20, 20), 2)
    cv2.imwrite(os.path.join(target_dir, "01_Genuine_Passport_With_MRZ.jpg"), p1)

    # 1B: Passenger Live Camera Matching Photo
    s1 = np.ones((320, 320, 3), dtype=np.uint8) * 238
    draw_portrait(s1, 60, 45, 190, hair_color=(30, 25, 20), skin_color=(215, 185, 165))
    cv2.imwrite(os.path.join(target_dir, "01_Genuine_Passport_Passenger_Selfie.jpg"), s1)

    # =========================================================================
    # SAMPLE 2: TAMPERED VISA STAMP
    # =========================================================================
    p2 = p1.copy()
    # Distort the visa stamp with heavy irregular geometry and ink bleed
    cv2.circle(p2, (605, 205), 58, (244, 244, 244), -1) # Erase clean stamp
    cv2.ellipse(p2, (605, 205), (65, 42), 35, 0, 360, (0, 0, 230), 4) # Distorted warped ellipse
    cv2.line(p2, (550, 180), (660, 235), (0, 0, 230), 2)
    cv2.putText(p2, "ALTERED VISA", (552, 202), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 0, 230), 2)
    cv2.putText(p2, "FORGED SEAL", (558, 222), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 0, 230), 1)
    # Ink bleed noise
    noise_stamp = np.random.randint(0, 120, (60, 80, 3), dtype=np.uint8)
    p2[175:235, 565:645] = cv2.addWeighted(p2[175:235, 565:645], 0.6, noise_stamp, 0.4, 0)
    cv2.imwrite(os.path.join(target_dir, "02_Tampered_Visa_Stamp.jpg"), p2)

    # =========================================================================
    # SAMPLE 3: MODIFIED DATE OF BIRTH (DOB)
    # =========================================================================
    p3 = p1.copy()
    # Spliced altered birth date block with font weight and bounding discontinuity
    cv2.rectangle(p3, (225, 206), (540, 238), (255, 255, 185), -1)
    cv2.rectangle(p3, (225, 206), (540, 238), (0, 0, 220), 2)
    cv2.putText(p3, "DATE OF BIRTH: 22 MAR 1988 [ALTERED]", (230, 228), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 200), 2)
    cv2.imwrite(os.path.join(target_dir, "03_Modified_Date_Of_Birth.jpg"), p3)

    # =========================================================================
    # SAMPLE 4: ALTERED PHOTOGRAPH (PHOTO REPLACEMENT / FACE-SWAP)
    # =========================================================================
    p4 = p1.copy()
    # Draw unnatural spliced rectangular photo patch with mismatched skin & hair
    cv2.rectangle(p4, (33, 86), (212, 317), (0, 0, 240), 3)
    cv2.rectangle(p4, (35, 88), (210, 315), (255, 240, 240), -1)
    draw_portrait(p4, 45, 100, 155, hair_color=(160, 40, 20), skin_color=(240, 210, 190), glasses=True)
    # Splicing artifact line around photo
    cv2.line(p4, (35, 88), (210, 88), (0, 0, 255), 2)
    cv2.putText(p4, "PHOTO REPLACED", (40, 335), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 0, 220), 2)
    cv2.imwrite(os.path.join(target_dir, "04_Altered_Photograph_Face_Swap.jpg"), p4)

    # =========================================================================
    # SAMPLE 5: IDENTITY IMPERSONATION (GENUINE DOC + IMPOSTOR TRAVELER)
    # =========================================================================
    # Genuine Passport of Traveler A
    p5 = p1.copy()
    cv2.imwrite(os.path.join(target_dir, "05_Identity_Impersonation_Passport.jpg"), p5)
    # Impostor Traveler B (Completely different facial structure, glasses, and beard)
    s5 = np.ones((320, 320, 3), dtype=np.uint8) * 230
    draw_portrait(s5, 60, 45, 190, hair_color=(140, 90, 40), skin_color=(235, 200, 180), glasses=True, beard=True)
    cv2.imwrite(os.path.join(target_dir, "05_Identity_Impersonation_Impostor_Selfie.jpg"), s5)

    # =========================================================================
    # SAMPLE 6: EXPIRED TRAVEL CREDENTIAL
    # =========================================================================
    p6 = p1.copy()
    cv2.rectangle(p6, (225, 244), (540, 274), (255, 230, 230), -1)
    cv2.putText(p6, "EXPIRY DATE: 10 JAN 2024 [EXPIRED]", (230, 264), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (180, 0, 0), 2)
    cv2.imwrite(os.path.join(target_dir, "06_Expired_Travel_Credential.jpg"), p6)

    # =========================================================================
    # SAMPLE 7: INTERPOL BLACKLISTED / STOLEN PASSPORT
    # =========================================================================
    p7 = p1.copy()
    cv2.rectangle(p7, (225, 100), (680, 132), (255, 225, 225), -1)
    cv2.putText(p7, "TYPE: P   CODE: UTO   PASSPORT NO: P-BLOCKED-902", (230, 118), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (190, 0, 0), 2)
    cv2.rectangle(p7, (225, 136), (680, 168), (255, 225, 225), -1)
    cv2.putText(p7, "SURNAME: WATCHLIST   GIVEN NAMES: SUSPECT", (230, 154), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (190, 0, 0), 2)
    cv2.imwrite(os.path.join(target_dir, "07_Interpol_Blacklisted_Stolen_Passport.jpg"), p7)

    # =========================================================================
    # SAMPLE 8: GENUINE NATIONAL CITIZEN ID
    # =========================================================================
    id8 = np.ones((400, 640, 3), dtype=np.uint8) * 245
    cv2.rectangle(id8, (0, 0), (640, 70), (35, 75, 130), -1)
    cv2.putText(id8, "CITIZEN IDENTITY CARD - NATIONAL CIVIL REGISTRY", (25, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)
    # Photo
    cv2.rectangle(id8, (40, 95), (200, 305), (210, 210, 210), -1)
    cv2.rectangle(id8, (40, 95), (200, 305), (80, 80, 80), 2)
    draw_portrait(id8, 50, 105, 140, hair_color=(35, 30, 25), skin_color=(220, 185, 165))
    # Bio
    cv2.putText(id8, "NAME: CITIZEN HOLDER", (225, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (30, 30, 30), 2)
    cv2.putText(id8, "DOCUMENT NO: ID-90214812", (225, 168), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (30, 30, 30), 2)
    cv2.putText(id8, "DOB: 18 JUN 1992", (225, 208), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (50, 50, 50), 2)
    cv2.putText(id8, "EXPIRY: 31 DEC 2030", (225, 248), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (50, 50, 50), 2)
    cv2.putText(id8, "STATUS: CITIZEN / FULL LEGAL RIGHTS", (225, 288), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 120, 20), 2)
    cv2.imwrite(os.path.join(target_dir, "08_Genuine_National_Citizen_ID.jpg"), id8)

    # 8B: Matching Citizen Selfie
    s8 = np.ones((300, 300, 3), dtype=np.uint8) * 235
    draw_portrait(s8, 60, 40, 180, hair_color=(35, 30, 25), skin_color=(220, 185, 165))
    cv2.imwrite(os.path.join(target_dir, "08_Genuine_National_ID_Selfie.jpg"), s8)

    # =========================================================================
    # SAMPLE 9: TAMPERED NATIONAL ID CARD
    # =========================================================================
    id9 = id8.copy()
    cv2.rectangle(id9, (220, 148), (590, 188), (255, 255, 185), -1)
    cv2.rectangle(id9, (220, 148), (590, 188), (0, 0, 220), 2)
    cv2.putText(id9, "DOCUMENT NO: ID-99482-INVALID", (225, 176), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 0, 190), 2)
    cv2.rectangle(id9, (220, 108), (560, 143), (255, 235, 235), -1)
    cv2.putText(id9, "NAME: ALTERED / FORGED USER", (225, 133), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (180, 0, 0), 2)
    cv2.imwrite(os.path.join(target_dir, "09_Tampered_National_ID_Card.jpg"), id9)

    # =========================================================================
    # SAMPLE 10: STATE DRIVER LICENSE
    # =========================================================================
    dl10 = np.ones((400, 640, 3), dtype=np.uint8) * 245
    cv2.rectangle(dl10, (0, 0), (640, 70), (25, 70, 105), -1)
    cv2.putText(dl10, "STATE DRIVER LICENSE - MOTOR VEHICLES DIVISION", (25, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)
    cv2.rectangle(dl10, (40, 95), (200, 305), (210, 210, 210), -1)
    cv2.rectangle(dl10, (40, 95), (200, 305), (80, 80, 80), 2)
    draw_portrait(dl10, 50, 105, 140, hair_color=(20, 20, 20), skin_color=(215, 180, 155))
    cv2.putText(dl10, "NAME: VERIFIED CITIZEN", (225, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (30, 30, 30), 2)
    cv2.putText(dl10, "LICENSE NO: DL-88219044", (225, 168), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (30, 30, 30), 2)
    cv2.putText(dl10, "DOB: 12 APR 1991", (225, 208), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (50, 50, 50), 2)
    cv2.putText(dl10, "CLASS: C - COMMERCIAL & PASSENGER", (225, 248), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (50, 50, 50), 2)
    cv2.putText(dl10, "EXPIRY: 24 JUL 2029", (225, 288), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (20, 120, 20), 2)
    cv2.imwrite(os.path.join(target_dir, "10_State_Driver_License.jpg"), dl10)

    # =========================================================================
    # SAMPLE 11: INTERNATIONAL TRAVEL PERMIT
    # =========================================================================
    pm11 = np.ones((400, 640, 3), dtype=np.uint8) * 242
    cv2.rectangle(pm11, (0, 0), (640, 70), (45, 30, 80), -1)
    cv2.putText(pm11, "CROSS-BORDER TRANSIT PERMIT - GATE PASS", (25, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)
    cv2.rectangle(pm11, (40, 95), (200, 305), (210, 210, 210), -1)
    cv2.rectangle(pm11, (40, 95), (200, 305), (80, 80, 80), 2)
    draw_portrait(pm11, 50, 105, 140, hair_color=(50, 40, 30), skin_color=(220, 190, 170))
    cv2.putText(pm11, "HOLDER: CONNOR, SARAH J.", (225, 128), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (30, 30, 30), 2)
    cv2.putText(pm11, "PERMIT ID: PRM-2026-8801", (225, 168), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (30, 30, 30), 2)
    cv2.putText(pm11, "AUTHORIZED ROUTE: GATE 4 - TRANSIT", (225, 208), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (50, 50, 50), 2)
    cv2.putText(pm11, "VALIDITY: 01 SEP 2026 - 31 OCT 2026", (225, 248), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (50, 50, 50), 2)
    cv2.putText(pm11, "STATUS: ACTIVE TRANSIT AUTHORIZATION", (225, 288), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (20, 120, 20), 2)
    cv2.imwrite(os.path.join(target_dir, "11_International_Travel_Permit.jpg"), pm11)

    print("All 11 criteria demo samples successfully generated in:", target_dir)

if __name__ == "__main__":
    target = r"C:\Users\P Rahul\OneDrive\Desktop\sample id sheld"
    create_board_samples(target)
