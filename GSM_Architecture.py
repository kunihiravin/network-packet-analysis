# ============================================================
# GSM ARCHITECTURE SIMULATOR
# ============================================================
# Features:
# 1. GSM network topology
# 2. Network connection validation
# 3. Network summary
# 4. Mobile-to-mobile call routing
# 5. External network call routing
# 6. Traffic channel allocation
# 7. Channel availability monitoring
# 8. Active call management
# 9. Call termination and channel release
# ============================================================


# ------------------------------------------------------------
# 1. DEFINE GSM NETWORK COMPONENTS
# ------------------------------------------------------------

def get_default_topology():

    network = {

        "MS": {
            "MS001": {"subscriber": "Subscriber 001", "bts": "BTS001"},
            "MS002": {"subscriber": "Subscriber 002", "bts": "BTS001"},
            "MS003": {"subscriber": "Subscriber 003", "bts": "BTS002"},
            "MS004": {"subscriber": "Subscriber 004", "bts": "BTS003"},
            "MS005": {"subscriber": "Subscriber 005", "bts": "BTS003"}
        },

        "BTS": {
            "BTS001": {
                "bsc": "BSC001",
                "channels": 5,
                "status": "Active"
            },

            "BTS002": {
                "bsc": "BSC001",
                "channels": 5,
                "status": "Active"
            },

            "BTS003": {
                "bsc": "BSC002",
                "channels": 5,
                "status": "Active"
            }
        },

        "BSC": {
            "BSC001": {"msc": "MSC001", "status": "Active"},
            "BSC002": {"msc": "MSC001", "status": "Active"}
        },

        "MSC": {
            "MSC001": {"gmsc": "GMSC001", "status": "Active"}
        },

        "GMSC": {
            "GMSC001": {"status": "Active"}
        },

        "HLR": {
            "HLR001": {"status": "Active"}
        },

        "VLR": {
            "VLR001": {"msc": "MSC001", "status": "Active"}
        }
    }

    # Runtime information for channel allocation and call tracking
    network["_runtime"] = {
        "active_calls": {},
        "next_call_number": 1
    }

    # Initialize occupied channels at each BTS
    for bts in network["BTS"].values():
        bts["occupied_channels"] = 0

    return network


# ------------------------------------------------------------
# 2. INITIALIZE RUNTIME INFORMATION
# ------------------------------------------------------------

def initialize_runtime(network):

    network.setdefault("_runtime", {
        "active_calls": {},
        "next_call_number": 1
    })

    for bts in network["BTS"].values():
        bts.setdefault("occupied_channels", 0)


# ------------------------------------------------------------
# 3. VALIDATE NETWORK CONNECTIONS
# ------------------------------------------------------------

def validate_topology(network):

    errors = []

    required_components = [
        "MS", "BTS", "BSC", "MSC", "GMSC", "HLR", "VLR"
    ]

    for component in required_components:

        if component not in network:
            errors.append(f"Missing network component: {component}")

    if errors:
        return errors

    # Validate mobile station connections
    for ms_id, ms in network["MS"].items():

        if ms.get("bts") not in network["BTS"]:
            errors.append(
                f"{ms_id} has no valid BTS connection."
            )

    # Validate BTS connections
    for bts_id, bts in network["BTS"].items():

        if bts.get("bsc") not in network["BSC"]:
            errors.append(
                f"{bts_id} has no valid BSC connection."
            )

        if bts.get("channels", 0) <= 0:
            errors.append(
                f"{bts_id} has an invalid channel capacity."
            )

    # Validate BSC connections
    for bsc_id, bsc in network["BSC"].items():

        if bsc.get("msc") not in network["MSC"]:
            errors.append(
                f"{bsc_id} has no valid MSC connection."
            )

    # Validate MSC connections
    for msc_id, msc in network["MSC"].items():

        if msc.get("gmsc") not in network["GMSC"]:
            errors.append(
                f"{msc_id} has no valid GMSC connection."
            )

    return errors


# ------------------------------------------------------------
# 4. GENERATE GSM NETWORK SUMMARY
# ------------------------------------------------------------

def network_summary(network):

    initialize_runtime(network)

    return {

        "mobile_subscribers": len(network["MS"]),

        "base_transceiver_stations": len(network["BTS"]),

        "base_station_controllers": len(network["BSC"]),

        "mobile_switching_centres": len(network["MSC"]),

        "gateway_msc": len(network["GMSC"]),

        "total_radio_channels": sum(
            bts["channels"]
            for bts in network["BTS"].values()
        ),

        "occupied_channels": sum(
            bts["occupied_channels"]
            for bts in network["BTS"].values()
        ),

        "available_channels": sum(
            bts["channels"] - bts["occupied_channels"]
            for bts in network["BTS"].values()
        ),

        "active_calls": len(
            network["_runtime"]["active_calls"]
        )
    }


# ------------------------------------------------------------
# 5. CHECK NETWORK COMPONENT STATUS
# ------------------------------------------------------------

def check_component(network, component_type, component_id):

    component = network[component_type].get(component_id)

    if component is None:
        return False, f"{component_id} does not exist."

    if component.get("status", "Active") != "Active":
        return False, f"{component_id} is unavailable."

    return True, "Available"


# ------------------------------------------------------------
# 6. GET BTS CHANNEL STATUS
# ------------------------------------------------------------

def get_channel_status(network):

    initialize_runtime(network)

    results = {}

    for bts_id, bts in network["BTS"].items():

        total = bts["channels"]
        occupied = bts["occupied_channels"]
        available = total - occupied

        utilization = (
            occupied / total
        ) * 100 if total > 0 else 0

        results[bts_id] = {

            "total_channels": total,

            "occupied_channels": occupied,

            "available_channels": available,

            "utilization_percent": round(utilization, 2),

            "status": bts["status"]
        }

    return results


# ------------------------------------------------------------
# 7. ALLOCATE BTS TRAFFIC CHANNELS
# ------------------------------------------------------------

def allocate_channels(network, bts_list):

    initialize_runtime(network)

    # Avoid allocating twice for the same BTS
    bts_list = list(dict.fromkeys(bts_list))

    # First check all BTSs before allocating anything
    for bts_id in bts_list:

        if bts_id not in network["BTS"]:
            return False, f"{bts_id} does not exist."

        bts = network["BTS"][bts_id]

        if bts["status"] != "Active":
            return False, f"{bts_id} is unavailable."

        if bts["occupied_channels"] >= bts["channels"]:
            return False, f"No available channels at {bts_id}."

    # Allocate one traffic channel at each required BTS
    for bts_id in bts_list:

        network["BTS"][bts_id]["occupied_channels"] += 1

    return True, "Traffic channels successfully allocated."


# ------------------------------------------------------------
# 8. RELEASE BTS TRAFFIC CHANNELS
# ------------------------------------------------------------

def release_channels(network, bts_list):

    initialize_runtime(network)

    bts_list = list(dict.fromkeys(bts_list))

    for bts_id in bts_list:

        if bts_id in network["BTS"]:

            bts = network["BTS"][bts_id]

            if bts["occupied_channels"] > 0:
                bts["occupied_channels"] -= 1


# ------------------------------------------------------------
# 9. START AND REGISTER A CALL
# ------------------------------------------------------------

def start_call(network, source_ms, destination, route, bts_list):

    initialize_runtime(network)

    success, message = allocate_channels(network, bts_list)

    if not success:

        return {
            "status": "Blocked",
            "reason": message,
            "source": source_ms,
            "destination": destination,
            "route": route
        }

    runtime = network["_runtime"]

    call_number = runtime["next_call_number"]

    call_id = f"CALL{call_number:04d}"

    runtime["next_call_number"] += 1

    runtime["active_calls"][call_id] = {

        "source": source_ms,

        "destination": destination,

        "route": route,

        "bts_list": list(dict.fromkeys(bts_list))

    }

    return {

        "status": "Successful",

        "call_id": call_id,

        "source": source_ms,

        "destination": destination,

        "route": route,

        "allocated_bts": list(dict.fromkeys(bts_list)),

        "message": "Call connected successfully."

    }


# ------------------------------------------------------------
# 10. TRACE A MOBILE-TO-MOBILE CALL
# ------------------------------------------------------------

def trace_call(network, source_ms, destination_ms):

    initialize_runtime(network)

    # Check mobile stations
    if source_ms not in network["MS"]:
        return {
            "status": "Failed",
            "reason": "Source mobile not found."
        }

    if destination_ms not in network["MS"]:
        return {
            "status": "Failed",
            "reason": "Destination mobile not found."
        }

    if source_ms == destination_ms:
        return {
            "status": "Failed",
            "reason": "Source and destination cannot be the same."
        }

    # Validate network connections
    errors = validate_topology(network)

    if errors:
        return {
            "status": "Failed",
            "reason": errors
        }

    source_bts = network["MS"][source_ms]["bts"]

    destination_bts = network["MS"][destination_ms]["bts"]

    source_bsc = network["BTS"][source_bts]["bsc"]

    destination_bsc = network["BTS"][destination_bts]["bsc"]

    source_msc = network["BSC"][source_bsc]["msc"]

    destination_msc = network["BSC"][destination_bsc]["msc"]

    # Check source and destination network components
    components = [

        ("BTS", source_bts),
        ("BSC", source_bsc),
        ("MSC", source_msc),

        ("BTS", destination_bts),
        ("BSC", destination_bsc),
        ("MSC", destination_msc)

    ]

    for component_type, component_id in components:

        available, message = check_component(
            network,
            component_type,
            component_id
        )

        if not available:
            return {
                "status": "Failed",
                "reason": message
            }

    # Inter-MSC routing is not yet implemented
    if source_msc != destination_msc:

        return {
            "status": "Failed",
            "reason": "Inter-MSC routing is not implemented."
        }

    route = [

        f"{source_ms} (Source Mobile)",

        f"{source_bts} (Source BTS)",

        f"{source_bsc} (Source BSC)",

        f"{source_msc} (MSC)",

        f"{destination_bsc} (Destination BSC)",

        f"{destination_bts} (Destination BTS)",

        f"{destination_ms} (Destination Mobile)"

    ]

    # Allocate radio resources and register the call
    return start_call(

        network,

        source_ms,

        destination_ms,

        route,

        [source_bts, destination_bts]

    )


# ------------------------------------------------------------
# 11. TRACE A CALL TO AN EXTERNAL NETWORK
# ------------------------------------------------------------

def trace_external_call(network, source_ms):

    initialize_runtime(network)

    if source_ms not in network["MS"]:

        return {
            "status": "Failed",
            "reason": "Source mobile not found."
        }

    errors = validate_topology(network)

    if errors:

        return {
            "status": "Failed",
            "reason": errors
        }

    source_bts = network["MS"][source_ms]["bts"]

    source_bsc = network["BTS"][source_bts]["bsc"]

    source_msc = network["BSC"][source_bsc]["msc"]

    gmsc = network["MSC"][source_msc]["gmsc"]

    components = [

        ("BTS", source_bts),

        ("BSC", source_bsc),

        ("MSC", source_msc),

        ("GMSC", gmsc)

    ]

    for component_type, component_id in components:

        available, message = check_component(

            network,

            component_type,

            component_id

        )

        if not available:

            return {
                "status": "Failed",
                "reason": message
            }

    route = [

        source_ms,

        source_bts,

        source_bsc,

        source_msc,

        gmsc,

        "External Telephone Network"

    ]

    return start_call(

        network,

        source_ms,

        "External Telephone Network",

        route,

        [source_bts]

    )


# ------------------------------------------------------------
# 12. TERMINATE A CALL
# ------------------------------------------------------------

def terminate_call(network, call_id):

    initialize_runtime(network)

    active_calls = network["_runtime"]["active_calls"]

    if call_id not in active_calls:

        return {
            "status": "Failed",
            "reason": "Call ID not found or call already terminated."
        }

    call = active_calls[call_id]

    # Release the allocated channels
    release_channels(network, call["bts_list"])

    # Remove call from active calls
    del active_calls[call_id]

    return {

        "status": "Successful",

        "call_id": call_id,

        "message": "Call terminated and channels released."

    }


# ------------------------------------------------------------
# 13. DISPLAY ACTIVE CALLS
# ------------------------------------------------------------

def get_active_calls(network):

    initialize_runtime(network)

    return network["_runtime"]["active_calls"]