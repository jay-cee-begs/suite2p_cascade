from dataclasses import dataclass

@dataclass
class AnalysisParams:

    overwrite_suite2p: bool = False
    overwrite_cacade: bool = False
    multivid_processing: bool = False
    use_suite2p_ROI_classifier: bool = False
    update_suite2p_iscell: bool = False
    Img_Overlay: str = "meanImg"

    cascade_activity_threshold: float = 0.1
    nb_neurons: int = 16
    model_name: str = "Global_EXC_10Hz_smoothing_200ms"

    baseline_correction: bool = False 
    correction_method: str = "airPLS"
    normalize_peaks: bool = False
    normalization_method: str = 'Cell'

    MAD_baseline_filter_threshold: float = 2.0
    activity_threshold: float = 0.1

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data: dict):
        return AnalysisParams(**data)