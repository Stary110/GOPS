#  Copyright (c). All Rights Reserved.
#  General Optimal control Problem Solver (GOPS)
#  Intelligent Driving Lab (iDLab), Tsinghua University
#
#  Creator: iDLab
#  Lab Leader: Prof. Shengbo Eben Li
#  Email: lisb04@gmail.com
#
#  Description: base wrapper for model type environments
#  Update: 2022-09-21, Yuhang Zhang: create base wrapper
#  Update: 2022-10-26, Yujie Yang: rewrite base wrapper


from typing import Tuple

import torch

from gops.env.env_ocp.env_model.pyth_base_model import PythBaseModel
from gops.utils.gops_typing import InfoDict


class ModelWrapper:
    """Base wrapper class for model type environment wrapper.

    :param PythBaseModel model: gops model type environment.
    """

    def __init__(self, model: PythBaseModel):
        self.model = model

    def forward(
        self,
        obs: torch.Tensor,
        action: torch.Tensor,
        done: torch.Tensor,
        info: InfoDict,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, InfoDict]:
        return self.model.forward(obs, action, done, info)

    def __getattr__(self, name):
        return getattr(self.model, name)

    @property
    def unwrapped(self):
        return self.model.unwrapped
