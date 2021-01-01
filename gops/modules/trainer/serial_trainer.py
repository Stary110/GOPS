#   Copyright (c) 2020 ocp-tools Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Author: Sun Hao


__all__ = ['SerialTrainer']

import numpy as np
import torch
from modules.create_pkg.create_buffer import create_buffer


class SerialTrainer():
    def __init__(self,alg,env,NOISE=0.05,REWARD_SCALE=0.1,BATCH_SIZE=32,TRAIN_EPISODE=5000,IS_RENDER=False,**kwargs):
        self.algo = alg
        self.env = env

        self.noise = NOISE
        self.reward_scale = REWARD_SCALE
        self.batch_size = BATCH_SIZE
        self.train_eposode = TRAIN_EPISODE
        self.render = IS_RENDER

        self.buffer = create_buffer(**kwargs)
        self.warm_size = kwargs['buffer_warm_size']
        # 创建网络
        # 定义优化器


    def run_episode(self):
        obs = self.env.reset()
        total_reward = 0
        steps = 0
        while True:
            steps += 1
            batch_obs = np.expand_dims(obs, axis=0)
            action = self.algo.predict(torch.from_numpy(batch_obs.astype('float32')))
            # 增加探索扰动, 输出限制在 [-1.0, 1.0] 范围内
            action = np.clip(np.random.normal(action, self.noise), -1.0, 1.0)
            next_obs, reward, done, info = self.env.step(action)
            action = [action]
            # store in buffer
            self.buffer.store(obs, action, self.reward_scale * reward, next_obs, done)
            # buffer size > warm size
            if self.buffer.size > self.warm_size and (steps % 5) == 0:
                batch = self.buffer.sample_batch(self.batch_size)
                self.algo.learn(data = batch)

            obs = next_obs
            total_reward += reward

            #print(self.algo.rpm.size)
            if done or steps >= 200:
                break
        return total_reward

    def evaluate(self):
        eval_reward = []
        for i in range(5):
            obs = self.env.reset()
            total_reward = 0
            steps = 0
            while True:
                batch_obs = np.expand_dims(obs, axis=0)
                action = self.algo.predict(batch_obs.astype('float32'))
                action = np.clip(action, -1.0, 1.0)

                steps += 1
                next_obs, reward, done, info = self.env.step(action)

                obs = next_obs
                total_reward += reward

                if self.render:
                    self.env.render()
                if done or steps >= 200:
                    break
            eval_reward.append(total_reward)
        return np.mean(eval_reward)


    def train(self):
        # 往经验池中预存数据
        while self.buffer.size < self.warm_size:
            self.run_episode()


        episode = 0
        while episode < self.train_eposode:
            for i in range(50):
                total_reward = self.run_episode()
                episode += 1

            print("total reward = ",total_reward)
