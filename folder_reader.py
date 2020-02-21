import os
import json
import pydicom
from pydicom import dcmread

print(pydicom.__version__)


class Instance(dict):
    def __init__(
        self, filepath, SOPInstanceUID, InstanceNumber, ImagePosition, ImageOrientation
    ):
        super().__init__()
        self.__dict__ = self
        self.SOPInstanceUID = SOPInstanceUID
        self.InstanceNumber = InstanceNumber
        self.ImagePosition = ImagePosition
        self.ImageOrientation = ImageOrientation
        self.filepath = filepath


class Series(dict):
    def __init__(self, SeriesInstanceUID, SeriesNumber, Modality, SeriesDescription):
        super().__init__()
        self.__dict__ = self
        self.SeriesInstanceUID = SeriesInstanceUID
        self.SeriesNumber = SeriesNumber
        self.Modality = Modality
        self.SeriesDescription = SeriesDescription
        self.children = []

    def add_child(self, instance):
        self.children.append(instance)

    def sort_children(self):
        pass

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.SeriesInstanceUID
        elif isinstance(other, Series):
            return other.SeriesInstanceUID == self.SeriesInstanceUID
        else:
            return NotImplemented


class Study(dict):
    def __init__(self, StudyInstanceUID, StudyID, StudyDate, StudyDescription):
        super().__init__()
        self.__dict__ = self
        self.StudyInstanceUID = StudyInstanceUID
        self.StudyID = StudyID
        self.StudyDate = StudyDate
        self.StudyDescription = StudyDescription
        self.children = []

    def add_child(self, series):
        self.children.append(series)

    def sort_children(self):
        pass

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.StudyInstanceUID
        elif isinstance(other, Study):
            return other.StudyInstanceUID == self.StudyInstanceUID
        else:
            return NotImplemented

    def get_child(self, SeriesInstanceUID):
        for series in self.children:
            if series == SeriesInstanceUID:
                return series
        return None


class Patient(dict):
    def __init__(self, PatientID, PatientName):
        super().__init__()
        self.__dict__ = self
        self.PatientID = PatientID
        self.PatientName = PatientName
        self.children = []

    def add_child(self, study):
        self.children.append(study)

    def sort_children(self):
        pass

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.PatientID
        elif isinstance(other, Patient):
            return other.PatientID == self.PatientID
        else:
            return NotImplemented

    def get_child(self, StudyInstanceUID):
        for study in self.children:
            if study == StudyInstanceUID:
                return study
        return None


class DicomFolder(dict):
    """
    A class representing all DCM files in a folder, similar to DicomDir

    References:
    https://pydicom.github.io/pydicom/stable/reference/generated/pydicom.dicomdir.DicomDir.html
    """

    def __init__(self):
        super().__init__()
        self.__dict__ = self
        self.patient_records = []

    def add_patient_record(self, patient):
        self.patient_records.append(patient)

    def sort_patient_records(self):
        pass

    def get_patient_record(self, PatientID):
        for patient_record in self.patient_records:
            if patient_record == PatientID:
                return patient_record
        return None

    def add_instance(self, instance):
        pass


def read_dicomfolder(foldername):
    """
    Scan a folder for DCM files and return a `DicomFolder`.
    Similar to `pydicom.filereader.read_dicomdir()`

    References:
    https://pydicom.github.io/pydicom/stable/reference/generated/pydicom.filereader.read_dicomdir.html
    https://pydicom.github.io/pydicom/stable/reference/generated/pydicom.dicomdir.DicomDir.html
    """
    dicomfolder = DicomFolder()
    for root, dirs, files in os.walk(foldername):
        for file in files:
            if not file.endswith(".dcm"):
                continue

            dcmname = os.path.join(root, file)
            # print(dcmname)
            try:
                ds = dcmread(dcmname, force=True)
                # instance attr
                SOPInstanceUID = ds.SOPInstanceUID
                InstanceNumber = (
                    int(ds.InstanceNumber) if hasattr(ds, "InstanceNumber") else None
                )
                ImagePosition = (
                    ds.ImagePosition if hasattr(ds, "ImagePosition") else None
                )
                ImageOrientation = (
                    ds.ImageOrientation if hasattr(ds, "ImageOrientation") else None
                )

                # series attr
                SeriesInstanceUID = ds.SeriesInstanceUID
                SeriesNumber = (
                    int(ds.SeriesNumber) if hasattr(ds, "SeriesNumber") else None
                )
                Modality = ds.Modality if hasattr(ds, "Modality") else None
                SeriesDescription = (
                    ds.SeriesDescription if hasattr(ds, "SeriesDescription") else None
                )

                # study attr
                StudyInstanceUID = ds.StudyInstanceUID
                StudyID = ds.StudyID if hasattr(ds, "StudyID") else None
                StudyDate = ds.StudyDate if hasattr(ds, "StudyDate") else None
                StudyDescription = (
                    ds.StudyDescription if hasattr(ds, "StudyDescription") else None
                )

                # patient attr
                PatientID = ds.PatientID if hasattr(ds, "PatientID") else "Anonymous"
                PatientName = ds.PatientName if hasattr(ds, "PatientName") else None

                # Insert into dicomfolder
                instance = Instance(
                    dcmname,
                    SOPInstanceUID,
                    InstanceNumber,
                    ImagePosition,
                    ImageOrientation,
                )
                patient = dicomfolder.get_patient_record(PatientID)
                if patient is None:
                    # print(patient)
                    series = Series(
                        SeriesInstanceUID, SeriesNumber, Modality, SeriesDescription
                    )
                    study = Study(
                        StudyInstanceUID, StudyID, StudyDate, StudyDescription
                    )
                    patient = Patient(PatientID, PatientName)
                    dicomfolder.add_patient_record(patient)
                    patient.add_child(study)
                    study.add_child(series)
                    series.add_child(instance)
                    continue

                study = patient.get_child(StudyInstanceUID)
                if study is None:
                    series = Series(
                        SeriesInstanceUID, SeriesNumber, Modality, SeriesDescription
                    )
                    study = Study(
                        StudyInstanceUID, StudyID, StudyDate, StudyDescription
                    )
                    patient.add_child(study)
                    study.add_child(series)
                    series.add_child(instance)
                    continue

                series = study.get_child(SeriesInstanceUID)
                if series is None:
                    series = Series(
                        SeriesInstanceUID, SeriesNumber, Modality, SeriesDescription
                    )
                    study.add_child(series)
                    series.add_child(instance)
                    continue

                series.add_child(instance)

            except pydicom.errors.InvalidDicomError as e:
                print(e)
                print(f"{dcmname} is not a valid DICOM file")

            # print(filepath, patient_id, patient_name, study_instance_uid, study_id, series_instance_uid, sop_instance_uid, instance_number,
            #     image_position, image_orientation)
    return dicomfolder


if __name__ == "__main__":
    # dicom_folder = "./siim-medical-images/"
    dicom_folder = "./Chest_CT_selected/"
    dicomfolder = read_dicomfolder(dicom_folder)
    print(dicomfolder)

    # print DicomFolder
    for patient in dicomfolder.patient_records:
        patient_id = patient.PatientID
        patient_name = patient.PatientName
        print(f"")
        print(f"patient_id: {patient_id}, patient_name: {patient_name}")

        for study in patient.children:
            study_uid = study.StudyInstanceUID
            study_id = study.StudyID
            study_date = study.StudyDate
            study_description = study.StudyDescription
            print(
                f"-- study_uid: {study_uid}, study_id: {study_id}, study_date: {study_date}, study_description: {study_description}"
            )

            for series in study.children:
                series_uid = series.SeriesInstanceUID
                modality = series.Modality
                series_number = series.SeriesNumber
                series_description = series.SeriesDescription
                print(
                    f"---- series_uid: {series_uid}, series_number: {series_number}, modality: {modality}, series_description: {series_description}"
                )

                for instance in series.children:
                    instance_uid = instance.SOPInstanceUID
                    instance_number = instance.InstanceNumber
                    image_position = instance.ImagePosition
                    image_orientation = instance.ImageOrientation
                    # print(f"instance_uid: {instance_uid}, instance_number: {instance_number}, image_position: {image_position}, image_orientation: {image_orientation}")

