from dataclasses import dataclass

from config.config_parsers.base_config_parsers import BaseConfig


@dataclass
class EmbedderInferConfig(BaseConfig):
    def to_structured_dict(self) -> dict:
        pass


@dataclass
class EmbedderInferIOConfig(EmbedderInferConfig):
    input_tiles_root: str
    coco_path: str
    output_folder: str

    @classmethod
    def from_dict(cls, config: dict):
        embedder_infer_io_config = config['embedder']['infer']['io']

        return cls(
            input_tiles_root=embedder_infer_io_config['input_tiles_root'],
            coco_path=embedder_infer_io_config['coco_path'],
            output_folder=embedder_infer_io_config['output_folder'],
        )

    def to_structured_dict(self):
        config = super().to_structured_dict()
        config['embedder']['infer']['io'] = {
            'input_tiles_root': self.input_tiles_root,
            'coco_path': self.coco_path,
            'output_folder': self.output_folder,
        }

        return config


@dataclass
class DINOv2InferConfig(EmbedderInferConfig):
    size: str

    @classmethod
    def from_dict(cls, config: dict):
        embedder_infer_config = config['embedder']['infer']
        dino_v2_config = embedder_infer_config['dino_v2']

        return cls(
            size=dino_v2_config['size'],
        )

    def to_structured_dict(self):
        config = {
            'embedder': {
                'dino_v2': {
                    'size': self.size,
                }
            }
        }

        return config


@dataclass
class DINOv2InferIOConfig(DINOv2InferConfig, EmbedderInferIOConfig):
    @classmethod
    def from_dict(cls, config: dict):
        embedder_infer_io_config = EmbedderInferIOConfig.from_dict(config)
        dinov2_config = DINOv2InferConfig.from_dict(config)

        return cls(
            **embedder_infer_io_config.as_dict(),
            **dinov2_config.as_dict(),
        )

    def to_structured_dict(self):
        embedder_infer_io_config = EmbedderInferIOConfig.to_structured_dict(self)
        dino_v2_config = DINOv2InferConfig.to_structured_dict(self)
        dino_v2_config['embedder']['infer']['io'] = embedder_infer_io_config['embedder']['infer']['io']
        return dino_v2_config
