from dataclasses import dataclass

@dataclass
class AnalysisParams:

    overwrite_suite2p: bool = False
    overwrite_cascade: bool = False
    multivid_processing: bool = False
    use_suite2p_ROI_classifier: bool = False
    update_suite2p_iscell: bool = True
    Img_Overlay: str = "meanImg"

    cascade_activity_threshold: float = 0.1
    nb_neurons: int = 16
    model_name: str = "Global_EXC_10Hz_smoothing_200ms"

    MAD_baseline_filter_threshold: float = 2.0
    baseline_correction: bool = False 
    correction_method: str = "airPLS"
    lambda_window: int = 100
    normalize_peaks: bool = False
    normalization_method: str = 'Cell'

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data: dict):
        return AnalysisParams(**data)