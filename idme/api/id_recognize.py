import json
import re
import os, shutil
import glob
from contextlib import contextmanager
from pathlib import Path
from django.conf import settings
import face_recognition
import google.generativeai as genai
import numpy as np
# from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.schema import UniqueConstraint

from .decorators import print_progress, log_exceptions, sleep_and_retry, limits, token_bucket

# DATABASE_URL = 'sqlite:///id_cards.db'
# Base = declarative_base()
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
GOOGLE_API_KEY = settings.GEMINIAPI_KEY
genai.configure(api_key=GOOGLE_API_KEY)

media_folder = settings.MEDIA_ROOT



# @contextmanager
# def get_db_session():
#     session = Session()
#     try:
#         yield session
#     except Exception as e:
#         session.rollback()
#         print(f"Error during database session: {e}")
#         raise
#     finally:
#         session.close()


# class IDCard(Base):
#     __tablename__ = 'id_cards'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String)
#     address = Column(String)
#     dob = Column(String)
#     expiry_date = Column(String)
#     license_number = Column(String, unique=True)
#     license_class = Column(String)
#     sex = Column(String)
#     height = Column(String)
#     weight = Column(String)
#     eyes = Column(String)
#     restrictions = Column(String)
#     endorsements = Column(String)
#     issue_date = Column(String)
#     donor = Column(String)
#     face_encoding = Column(LargeBinary, unique=True)
#
#     __table_args__ = (
#         UniqueConstraint('license_number', name='unique_license_number'),
#         UniqueConstraint('face_encoding', name='unique_face_encoding')
#     )
#
#
# Base.metadata.create_all(engine)


class GenerativeAI:
    def __init__(self, model_name):
        self.model = genai.GenerativeModel(model_name)

    @staticmethod
    def upload_file(file_path):
        return genai.upload_file(file_path)

    def generate_content(self, file, prompt):
        return self.model.generate_content([file, "\n\n", prompt])


def clean_result_text(result_text):
    cleaned_text = re.sub(r'```json|```', '', result_text).strip()
    try:
        json.loads(cleaned_text)
    except json.JSONDecodeError:
        cleaned_text = re.sub(r'\\n', ' ', cleaned_text)
        cleaned_text = re.sub(r'\\', '', cleaned_text)
    return cleaned_text


def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    if face_encodings:
        return face_encodings[0]
    return None


# @log_exceptions
# def save_to_database(data, face_encoding):
#     with get_db_session() as session:
#         try:
#             existing_record = session.query(IDCard).filter_by(
#                 license_number=data.get("Driver's License Number")).first()
#             if existing_record:
#                 print(f"Duplicate entry detected: {existing_record.license_number}. Skipping save.")
#                 return
#
#             existing_faces = session.query(IDCard).all()
#             existing_encodings = [np.frombuffer(face.face_encoding, dtype=np.float64) for face in existing_faces]
#             if any(face_recognition.compare_faces(existing_encodings, face_encoding, tolerance=0.6)):
#                 print("Duplicate face detected. Skipping save.")
#                 return
#
#             id_card = IDCard(
#                 name=data.get("Name"),
#                 address=data.get("Address"),
#                 dob=data.get("Date of Birth (DOB)"),
#                 expiry_date=data.get("Expiration Date (EXP)"),
#                 license_number=data.get("Driver's License Number"),
#                 license_class=data.get("Class"),
#                 sex=data.get("Sex"),
#                 height=data.get("Height"),
#                 weight=data.get("Weight"),
#                 eyes=data.get("Eyes"),
#                 restrictions=data.get("Restrictions"),
#                 endorsements=data.get("Endorsements"),
#                 issue_date=data.get("Issue Date"),
#                 donor=data.get("Donor"),
#                 face_encoding=face_encoding.tobytes()
#             )
#             session.add(id_card)
#             session.commit()
#             print("ID card information saved to database.")
#         except Exception as e:
#             session.rollback()
#             print(f"Error saving to database: {e}")
#

@log_exceptions
@sleep_and_retry
@limits(calls=2000, period=60)
@token_bucket(rate=10, capacity=100)
def process_id_card(file_path, generative_ai, prompt):
    print(f"Processing file: {file_path}")
    uploaded_file = generative_ai.upload_file(file_path)
    result = generative_ai.generate_content(uploaded_file, prompt)

    if result.text:
        result_text = clean_result_text(result.text)
        try:
            result_json = json.loads(result_text)
            print(json.dumps(result_json, indent=4))
            face_encoding = encode_face(file_path)
            data = result_json
            name = data.get("Name")
            address = data.get("Address")
            dob = data.get("Date of Birth (DOB)")
            expiry_date = data.get("Expiration Date (EXP)")
            license_number = data.get("Driver's License Number")
            license_class = data.get("Class")
            sex = data.get("Sex")
            height = data.get("Height")
            weight = data.get("Weight")
            eyes = data.get("Eyes")
            restrictions = data.get("Restrictions")
            endorsements = data.get("Endorsements")
            issue_date = data.get("Issue Date")
            donor = data.get("Donor")
            if face_encoding is not None:
                # save_to_database(result_json, face_encoding)

                face_encoding = face_encoding.tobytes()
                pass
            else:
                print(f"No face encoding found for {file_path}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Result text: {result_text}")
    else:
        print(f"No content generated for {file_path}")


@log_exceptions
@sleep_and_retry
@limits(calls=2000, period=60)
@token_bucket(rate=10, capacity=100)
def process_card_id(file_path, generative_ai, prompt):

    # media_path = Path(media_folder + "/id_cards" + file_path)
    print(f"Processing file: {file_path}")
    uploaded_file = generative_ai.upload_file(file_path)
    result = generative_ai.generate_content(uploaded_file, prompt)
    deletefile(file_path)
    if result.text:
        result_text = clean_result_text(result.text)
        try:
            result_json = json.loads(result_text)
            return result_json
        except json.JSONDecodeError as e:
            return result_text


# @print_progress
def idrecognize(client):
    media_path = Path(media_folder + "/id_cards/user_" + client)
    print(media_path)
    prompt = (
        "Please extract and parse the text from the ID card image. "
        "Ensure the extracted information is formatted for database entry with the following fields: "
        "Name, Address, Date of Birth (DOB), Expiration Date (EXP), and any other relevant details. "
        "Provide the output in a structured JSON format without any backticks. "
        "Example format: "
        "{"
        "\"Name\": \"John Doe\", "
        "\"Address\": \"123 Main St, Any town, USA\", "
        "\"Date of Birth (DOB)\": \"01/01/1970\", "
        "\"Expiration Date (EXP)\": \"01/01/2030\", "
        "\"Driver's License Number\": \"D1234567\", "
        "\"Class\": \"C\", "
        "\"Sex\": \"M\", "
        "\"Height\": \"6'-0\"\", "
        "\"Weight\": \"180 lb\", "
        "\"Eyes\": \"BLU\", "
        "\"Restrictions\": \"NONE\", "
        "\"Endorsements\": \"NONE\", "
        "\"Issue Date\": \"01/01/2020\", "
        "\"Donor\": \"Yes\""
        "}"
    )
    # print("Step 0")
    generative_ai = GenerativeAI("gemini-1.5-flash")
    # print("Step 1")
    # for file_path in glob.glob(media_path, recursive=True):
    for file_path in media_path.glob("*.jpg"):
        print(file_path.name)
        result = process_card_id(file_path, generative_ai, prompt)
    return result

#
# if __name__ == "__main__":
#     main()

def deletefile(file_path):
  try:
    if os.path.isfile(file_path) or os.path.islink(file_path):
      os.unlink(file_path)
    elif os.path.isdir(file_path):
      shutil.rmtree(file_path)
  except Exception as e:
    print('Failed to delete %s. Reason: %s' % (file_path, e))