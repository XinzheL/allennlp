from os import PathLike
from typing import Union, List, Callable, Optional, Dict, Any

from torch import FloatTensor

from allennlp.common.registrable import Registrable

OnePath = Union[str, PathLike]
ManyPaths = List[OnePath]


class ImageLoader(Registrable, Callable[[Union[OnePath, ManyPaths]], FloatTensor]):
    """
    An `ImageLoader` is a callable that takes as input one or more filenames, and outputs an image tensor of shape
    (batch, color, height, width).
    """

    default_implementation = "detectron"

    def __call__(
        self, filename_or_filenames: Union[OnePath, ManyPaths]
    ) -> Union[FloatTensor, List[FloatTensor]]:
        if not isinstance(filename_or_filenames, list):
            return self([filename_or_filenames])[0]

        from allennlp.common.file_utils import cached_path

        filenames = [cached_path(f) for f in filename_or_filenames]

        return self.load(filenames)

    def load(self, filenames: ManyPaths) -> List[FloatTensor]:
        raise NotImplementedError()


@ImageLoader.register("detectron")
class DetectronImageLoader(ImageLoader):
    def __init__(
        self,
        builtin_config_file: Optional[str] = None,
        yaml_config_file: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ):
        from allennlp.common.detectron import get_detectron_cfg

        cfg = get_detectron_cfg(builtin_config_file, yaml_config_file, overrides)

        from detectron2.data import DatasetMapper

        self.mapper = DatasetMapper(cfg)

    def load(self, filenames: ManyPaths) -> List[FloatTensor]:
        images = [{"file_name": str(f)} for f in filenames]
        images = [self.mapper(i) for i in images]
        images = [i["image"] for i in images]
        return images