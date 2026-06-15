from dataclasses import dataclass, field

@dataclass
class GraphParams:
    
    Spike_Histogram: bool = False
    total_estimated_spikes_per_frame: bool = True
    avg_estimated_spikes_per_frame: bool = True
    raster_plots: bool = True
    



    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data: dict):
        return GraphParams(**data)