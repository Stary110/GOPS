import torch

PI = 3.1415926
tensor_pi = torch.tensor(PI)


class GymPendulumDiff:
    def __init__(self):
        self.max_speed = 8
        self.max_torque = 2.
        self.dt = 0.05
        self.g = 10.0
        self.m = 1.
        self.l = 1.


    def step(self, state, u):
        """the state transformation function

        Parameters
        ----------
        state : [cos(theta), sin(theta), theta]
            shape:(3,)
        u : [torque]
            shape(1,)

        Returns
        -------
        newstate : shape:(3,)
        reward: shape : (1,)
        """
        costh, sinth, thdot = state

        th = arccs(sinth, costh)

        g = self.g
        m = self.m
        l = self.l
        dt = self.dt

        u = torch.clamp(u, -self.max_torque, self.max_torque)[0]
        self.costs = angle_normalize(th) ** 2 + .1 * thdot ** 2 + .001 * (u ** 2)

        newthdot = thdot + (-3 * g / (2 * l) * torch.sin(th + tensor_pi) + 3. / (m * l ** 2) * u) * dt
        newth = th + newthdot * dt
        newthdot = torch.clamp(newthdot, -self.max_speed, self.max_speed)
        newcosth = torch.cos(newth)
        newsinth = torch.sin(newth)
        state_new = torch.stack([newcosth, newsinth, newthdot])
        return state_new, self.costs

    def __call__(self, state, u):
        return self.step(state, u)


# def env_creator():
#     return GymPendulumDiff()


def clip_by_tensor(t, t_min, t_max):
    """
    clip_by_tensor
    :param t: tensor
    :param t_min: min
    :param t_max: max
    :return: cliped tensor
    """
    t = t.float()
    t_min = t_min.float()
    t_max = t_max.float()

    result = (t >= t_min).float() * t + (t < t_min).float() * t_min
    result = (result <= t_max).float() * result + (result > t_max).float() * t_max
    return result


def angle_normalize(x):
    return (((x + tensor_pi) % (2*tensor_pi)) - tensor_pi)


def arccs(sinth, costh):
    th = torch.acos(costh)
    if sinth <= 0:
        th = 2 * 3.1415926 - th
    return th





if __name__ == "__main__":
    f = PendulumDifferential()
    import gym
    import matplotlib.pyplot as plt
    import numpy as np
    env = gym.make('Pendulum-v0')
    s = env.reset()
    s_real = []
    s_fake = []
    for i in range(200):
        a = env.action_space.sample()
        sp, r, d, _ = env.step(a)
        # print(s, a, sp)
        s_real.append(sp)
        tsp, _ = f(torch.tensor(s), torch.tensor(a))
        s_fake.append(tsp.numpy())
        s = sp
    # print(tsp)
    s_real = np.array(s_real)
    s_fake = np.array(s_fake)
    plt.plot(s_real)
    plt.plot(s_fake)
    plt.show()
    print("All states match, The model is right")