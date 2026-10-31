import math

# ==========================================
# 1. M/M/1 QUEUING MODEL
# ==========================================

def mm1_model(arrival_rate, service_rate):

    lam = arrival_rate
    mu = service_rate

    if lam < 0 or mu <= 0:
        raise ValueError("Arrival rate must be non-negative and service rate positive.")

    if lam >= mu:
        return {
            "stable": False,
            "message": "System is unstable. Arrival rate must be less than service rate."
        }

    rho = lam / mu

    # Probability of zero customers
    P0 = 1 - rho

    # Average number in queue
    Lq = (lam ** 2) / (mu * (mu - lam))

    # Average number in system
    L = lam / (mu - lam)

    # Average waiting time in queue
    Wq = lam / (mu * (mu - lam))

    # Average time in system
    W = 1 / (mu - lam)

    # System capacity
    capacity = mu

    return {
        "stable": True,
        "arrival_rate": lam,
        "service_rate": mu,
        "utilization": rho,
        "traffic_intensity": rho,
        "P0": P0,
        "Lq": Lq,
        "L": L,
        "Wq": Wq,
        "W": W,
        "capacity": capacity
    }


# ==========================================
# 2. M/M/S QUEUING MODEL
# ==========================================

def mms_model(arrival_rate, service_rate, servers):

    lam = arrival_rate
    mu = service_rate
    s = servers

    if lam < 0 or mu <= 0 or s < 1:
        raise ValueError("Invalid queue parameters.")

    if lam >= s * mu:
        return {
            "stable": False,
            "message": "System is unstable. Increase the number of channels."
        }

    # Offered traffic in Erlangs
    A = lam / mu

    # Utilization per channel
    rho = A / s

    # Calculate P0
    summation = sum(
        (A ** n) / math.factorial(n)
        for n in range(s)
    )

    last_term = (
        (A ** s) /
        (math.factorial(s) * (1 - rho))
    )

    P0 = 1 / (summation + last_term)

    # Probability that an arriving call must wait
    P_wait = last_term * P0

    # Average queue length
    Lq = P_wait * rho / (1 - rho)

    # Average waiting time in queue
    Wq = Lq / lam if lam > 0 else 0

    # Average time in the system
    W = Wq + (1 / mu)

    # Average number of calls in the system
    L = lam * W

    # Total system capacity
    capacity = s * mu

    return {
        "stable": True,
        "arrival_rate": lam,
        "service_rate": mu,
        "servers": s,
        "traffic_intensity": A,
        "utilization": rho,
        "P0": P0,
        "P_wait": P_wait,
        "Lq": Lq,
        "L": L,
        "Wq": Wq,
        "W": W,
        "capacity": capacity
    }


# ==========================================
# 3. REQUIRED NUMBER OF CHANNELS
# ==========================================

def required_channels(arrival_rate, service_rate, target_utilization=0.8):

    if arrival_rate < 0 or service_rate <= 0:
        raise ValueError("Invalid traffic parameters.")

    if not 0 < target_utilization < 1:
        raise ValueError("Target utilization must be between 0 and 1.")

    if arrival_rate == 0:
        return 1

    channels = math.ceil(
        arrival_rate / (service_rate * target_utilization)
    )

    return max(1, channels)

import simpy
import random


def gsm_call_simulation(
        arrival_rate=8,
        service_rate=10,
        channels=5,
        total_calls=1000,
        simulation_mode="queue",
        seed=42
):
    """
    Simulates GSM call traffic using SimPy.

    arrival_rate: Incoming calls per minute.
    service_rate: Calls served per minute per channel.
    channels: Number of available traffic channels.
    total_calls: Number of calls generated.
    simulation_mode: 'queue' or 'blocking'.
    seed: Random seed for reproducibility.
    """

    if arrival_rate <= 0 or service_rate <= 0:
        raise ValueError("Arrival and service rates must be positive.")

    if channels < 1 or total_calls < 1:
        raise ValueError("Channels and total calls must be positive.")

    if simulation_mode not in ("queue", "blocking"):
        raise ValueError("Mode must be 'queue' or 'blocking'.")

    random.seed(seed)

    env = simpy.Environment()

    # Available GSM traffic channels
    bts_channels = simpy.Resource(
        env,
        capacity=channels
    )

    results = {
        "generated": 0,
        "successful": 0,
        "blocked": 0,
        "waiting_times": [],
        "call_durations": [],
        "busy_channel_time": 0,
        "queue_lengths": []
    }

    def gsm_call(call_id):

        arrival_time = env.now

        results["generated"] += 1

        results["queue_lengths"].append(
            (env.now, len(bts_channels.queue))
        )

        # Blocking model: reject call if all channels are occupied
        if simulation_mode == "blocking":

            if bts_channels.count >= channels:
                results["blocked"] += 1
                return

        # Request an available traffic channel
        with bts_channels.request() as request:

            yield request

            waiting_time = env.now - arrival_time

            results["waiting_times"].append(waiting_time)

            results["successful"] += 1

            # Generate call duration using exponential distribution
            call_duration = random.expovariate(service_rate)

            results["call_durations"].append(call_duration)

            yield env.timeout(call_duration)

            results["busy_channel_time"] += call_duration

    def call_generator():

        for call_id in range(total_calls):

            # Exponentially distributed inter-arrival time
            inter_arrival = random.expovariate(arrival_rate)

            yield env.timeout(inter_arrival)

            env.process(gsm_call(call_id))

    # Run the simulation
    env.process(call_generator())

    env.run()

    # Calculate results
    generated = results["generated"]
    successful = results["successful"]
    blocked = results["blocked"]

    blocking_probability = (
        blocked / generated * 100
        if generated > 0 else 0
    )

    average_waiting_time = (
        sum(results["waiting_times"]) /
        len(results["waiting_times"])
        if results["waiting_times"] else 0
    )

    average_call_duration = (
        sum(results["call_durations"]) /
        len(results["call_durations"])
        if results["call_durations"] else 0
    )

    # Approximate average number of occupied channels
    total_simulation_time = env.now

    channel_utilization = (
        results["busy_channel_time"] /
        (channels * total_simulation_time) * 100
        if total_simulation_time > 0 else 0
    )

    return {
        "mode": simulation_mode,
        "generated_calls": generated,
        "successful_calls": successful,
        "blocked_calls": blocked,
        "blocking_probability": blocking_probability,
        "average_waiting_time_seconds": average_waiting_time * 60,
        "average_call_duration_seconds": average_call_duration * 60,
        "channel_utilization_percent": channel_utilization,
        "simulation_time_minutes": total_simulation_time
    }
import math


def erlang_b(arrival_rate, service_rate, channels):
    """
    Calculates theoretical GSM call blocking probability.
    """

    A = arrival_rate / service_rate

    B = 1.0

    for n in range(1, channels + 1):
        B = (A * B) / (n + A * B)

    return B


def erlang_c(arrival_rate, service_rate, channels):
    """
    Calculates theoretical M/M/S queue performance.
    """

    A = arrival_rate / service_rate

    rho = A / channels

    if rho >= 1:
        raise ValueError("System is unstable. Add more channels.")

    summation = sum(
        (A ** n) / math.factorial(n)
        for n in range(channels)
    )

    last_term = (
        (A ** channels) /
        (math.factorial(channels) * (1 - rho))
    )

    P0 = 1 / (summation + last_term)

    P_wait = last_term * P0

    Wq = P_wait / (
        channels * service_rate - arrival_rate
    )

    Lq = arrival_rate * Wq

    return {
        "offered_traffic_erlangs": A,
        "utilization_percent": rho * 100,
        "probability_of_waiting_percent": P_wait * 100,
        "average_queue_length": Lq,
        "average_waiting_time_seconds": Wq * 60
    }
