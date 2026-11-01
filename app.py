import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import uuid
import tempfile

from datetime import date, timedelta

import Task_3_Network as Network
import Task_2_Traffic as Traffic
import GSM_Architecture as GSM

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Telecom Network Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CUSTOM DASHBOARD STYLE
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

[data-testid="stSidebar"] {
    background-color: #10243a;
}

[data-testid="stSidebar"] * {
    color: white;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e0e5ec;
}

h1, h2, h3 {
    color: #16324f;
}

.stButton > button {
    background-color: #1769aa;
    color: white;
    border-radius: 7px;
    border: none;
    padding: 8px 20px;
}

.stButton > button:hover {
    background-color: #0d4778;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. MAIN SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("📡 GSM PROJECT")
st.sidebar.caption("Telecommunications Network Management")

st.sidebar.divider()

selected_module = st.sidebar.radio(
    "MAIN NAVIGATION",
    [
        "Dashboard Overview",
        "GSM Architecture",
        "Network Benchmarking",
        "GSM Traffic Simulation",
        "Installation and Maintenance"
    ],
    key="main_navigation"
)

# ============================================================
# 4. MAIN DASHBOARD HEADER
# ============================================================

st.title("📡 TELECOMMUNICATION NETWORK MONITOR")

st.caption(
    "GSM Network Performance, Traffic Analysis, "
    "Equipment Installation and Maintenance"
)

st.divider()


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================

def safe_metric(value, unit=""):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):.2f}{unit}"

    except (ValueError, TypeError):
        return str(value)


def load_csv(filename, columns):

    if os.path.exists(filename):

        try:
            data = pd.read_csv(filename)

            for column in columns:

                if column not in data.columns:
                    data[column] = None

            return data[columns]

        except pd.errors.EmptyDataError:
            pass

    return pd.DataFrame(columns=columns)


def save_csv(data, filename):

    data.to_csv(filename, index=False)


def display_dataframe(data):

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 6. INSTALLATION DATA STORAGE
# ============================================================

DATA_FOLDER = "installation_data"

os.makedirs(DATA_FOLDER, exist_ok=True)

EQUIPMENT_FILE = os.path.join(
    DATA_FOLDER, "equipment.csv"
)

CHECKLIST_FILE = os.path.join(
    DATA_FOLDER, "installation_checklist.csv"
)

MAINTENANCE_FILE = os.path.join(
    DATA_FOLDER, "maintenance.csv"
)

INSPECTION_FILE = os.path.join(
    DATA_FOLDER, "inspections.csv"
)


equipment_columns = [
    "Equipment ID",
    "Equipment Name",
    "Category",
    "Location",
    "Quantity",
    "Installation Date",
    "Status"
]

checklist_columns = [
    "Equipment ID",
    "Activity",
    "Status",
    "Remarks",
    "Date"
]

maintenance_columns = [
    "Maintenance ID",
    "Equipment ID",
    "Equipment Name",
    "Maintenance Activity",
    "Scheduled Date",
    "Frequency",
    "Status"
]

inspection_columns = [
    "Inspection ID",
    "Equipment ID",
    "Equipment Name",
    "Inspection Date",
    "Condition",
    "Fault Description",
    "Corrective Action"
]


equipment = load_csv(
    EQUIPMENT_FILE,
    equipment_columns
)

checklist = load_csv(
    CHECKLIST_FILE,
    checklist_columns
)

maintenance = load_csv(
    MAINTENANCE_FILE,
    maintenance_columns
)

inspections = load_csv(
    INSPECTION_FILE,
    inspection_columns
)


# ============================================================
# 7. DASHBOARD OVERVIEW
# ============================================================

if selected_module == "Dashboard Overview":

    st.header("System Overview")

    st.write(
        "Welcome to the GSM Telecommunications Network "
        "Monitoring and Simulation System."
    )

    st.divider()

    total_equipment = len(equipment)

    installed = (
        len(equipment[equipment["Status"] == "Installed"])
        if not equipment.empty else 0
    )

    pending = (
        len(equipment[equipment["Status"] == "Pending"])
        if not equipment.empty else 0
    )

    total_maintenance = len(maintenance)

    overdue = 0

    if not maintenance.empty:

        dates = pd.to_datetime(
            maintenance["Scheduled Date"],
            errors="coerce"
        )

        overdue = len(
            maintenance[
                (maintenance["Status"] == "Pending") &
                (dates < pd.Timestamp(date.today()))
            ]
        )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Equipment Records",
        total_equipment
    )

    col2.metric(
        "Installed Equipment",
        installed
    )

    col3.metric(
        "Pending Equipment",
        pending
    )

    col4.metric(
        "Overdue Maintenance",
        overdue
    )

    st.divider()

    st.subheader("Project Modules")

    col1, col2 = st.columns(2)

    with col1:

        st.info("### 📊 Network Benchmarking")

        st.write(
            "Measure network latency, jitter, packet loss "
            "and throughput using ping testing and packet captures."
        )

        st.info("### 📞 GSM Traffic Simulation")

        st.write(
            "Evaluate GSM call traffic using M/M/1, M/M/S, "
            "Erlang B, Erlang C and SimPy."
        )

    with col2:

        st.info("### 🏗️ Installation Management")

        st.write(
            "Register BTS equipment and monitor installation activities."
        )

        st.info("### 🔧 Preventive Maintenance")

        st.write(
            "Schedule equipment maintenance and record inspections "
            "and faults."
        )

    st.divider()

    st.subheader("Equipment Installation Status")

    if not equipment.empty:

        status_counts = equipment["Status"].value_counts()

        st.bar_chart(status_counts)

        display_dataframe(equipment)

    else:

        st.info(
            "No equipment registered yet. "
            "Open Installation and Maintenance to begin."
        )

    st.divider()

    st.subheader("Maintenance Alerts")

    if not maintenance.empty:

        pending_maintenance = maintenance[
            maintenance["Status"] == "Pending"
        ].copy()

        pending_dates = pd.to_datetime(
            pending_maintenance["Scheduled Date"],
            errors="coerce"
        )

        overdue_records = pending_maintenance[
            pending_dates < pd.Timestamp(date.today())
        ]

        upcoming_records = pending_maintenance[
            pending_dates >= pd.Timestamp(date.today())
        ]

        if not overdue_records.empty:

            st.error(
                f"{len(overdue_records)} maintenance activity/activities "
                "are overdue."
            )

            display_dataframe(overdue_records)

        if not upcoming_records.empty:

            st.info("Upcoming Maintenance")

            display_dataframe(
                upcoming_records.sort_values("Scheduled Date")
            )

        if pending_maintenance.empty:

            st.success("No pending maintenance activities.")

    else:

        st.info("No maintenance schedules available.")

# ============================================================
# 8. GSM ARCHITECTURE MODULE
# ============================================================

elif selected_module == "GSM Architecture":

    st.header("📡 GSM NETWORK ARCHITECTURE")

    st.caption(
        "GSM Network Components, Call Routing, "
        "Radio Channel Allocation and Monitoring"
    )

    # --------------------------------------------------------
    # INITIALIZE GSM NETWORK
    # --------------------------------------------------------

    if "gsm_network" not in st.session_state:

        network = GSM.get_default_topology()

        GSM.initialize_runtime(network)

        st.session_state["gsm_network"] = network

    network = st.session_state["gsm_network"]

    # --------------------------------------------------------
    # ARCHITECTURE SUBMENU
    # --------------------------------------------------------

    architecture_page = st.sidebar.radio(
        "GSM ARCHITECTURE MENU",
        [
            "Network Overview",
            "Network Components",
            "Mobile-to-Mobile Call",
            "External Call",
            "Channel Monitoring",
            "Active Calls"
        ],
        key="architecture_navigation"
    )

    st.divider()

    # --------------------------------------------------------
    # PAGE 1: NETWORK OVERVIEW
    # --------------------------------------------------------

    if architecture_page == "Network Overview":

        st.subheader("GSM Network Overview")

        summary = GSM.network_summary(network)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Mobile Subscribers",
            summary["mobile_subscribers"]
        )

        col2.metric(
            "Base Transceiver Stations",
            summary["base_transceiver_stations"]
        )

        col3.metric(
            "Base Station Controllers",
            summary["base_station_controllers"]
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Mobile Switching Centres",
            summary["mobile_switching_centres"]
        )

        col2.metric(
            "Total Radio Channels",
            summary["total_radio_channels"]
        )

        col3.metric(
            "Active Calls",
            summary["active_calls"]
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Occupied Channels",
            summary["occupied_channels"]
        )

        col2.metric(
            "Available Channels",
            summary["available_channels"]
        )

        col3.metric(
            "Gateway MSC",
            summary["gateway_msc"]
        )

        st.divider()

        st.subheader("Logical GSM Network Structure")

        st.markdown("""
        ```text
                   MOBILE STATIONS
                  MS001  MS002  MS003
                       |
                       v
              BASE TRANSCEIVER STATIONS
                  BTS001  BTS002  BTS003
                       |
                       v
              BASE STATION CONTROLLERS
                     BSC001
                     BSC002
                       |
                       v
              MOBILE SWITCHING CENTRE
                      MSC001
                       |
                 +-----+------+
                 |            |
                 v            v
                HLR          VLR
                       |
                       v
              GATEWAY MSC
                    GMSC001
                       |
                       v
               EXTERNAL NETWORK
        ```
        """)

        st.info(
            "The architecture represents the logical GSM call path. "
            "The HLR and VLR provide subscriber information and "
            "location-related services."
        )

        st.divider()

        st.subheader("Topology Validation")

        validation = GSM.validate_topology(network)

        if not validation:

            st.success("GSM topology validation successful.")

        else:

            for issue in validation:

                st.error(issue)

    # --------------------------------------------------------
    # PAGE 2: NETWORK COMPONENTS
    # --------------------------------------------------------

    elif architecture_page == "Network Components":

        st.subheader("GSM Network Components")

        component_types = [
            "MS",
            "BTS",
            "BSC",
            "MSC",
            "GMSC",
            "HLR",
            "VLR"
        ]

        selected_component = st.selectbox(
            "Select Network Component",
            component_types
        )

        component_data = network[selected_component]

        st.write(
            f"### {selected_component} Equipment Records"
        )

        component_df = pd.DataFrame.from_dict(
            component_data,
            orient="index"
        )

        component_df.index.name = "Component ID"

        component_df = component_df.reset_index()

        st.dataframe(
            component_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Component Summary")

        st.metric(
            "Number of Components",
            len(component_data)
        )

    # --------------------------------------------------------
    # PAGE 3: MOBILE-TO-MOBILE CALL
    # --------------------------------------------------------

    elif architecture_page == "Mobile-to-Mobile Call":

        st.subheader("Mobile-to-Mobile Call Establishment")

        st.write(
            "Select two mobile subscribers to establish a "
            "simulated GSM call."
        )

        mobile_stations = list(network["MS"].keys())

        col1, col2 = st.columns(2)

        with col1:

            source_ms = st.selectbox(
                "Calling Mobile Station",
                mobile_stations,
                key="source_mobile"
            )

        with col2:

            destination_ms = st.selectbox(
                "Receiving Mobile Station",
                mobile_stations,
                key="destination_mobile"
            )

        if st.button("📞 ESTABLISH MOBILE CALL"):

            if source_ms == destination_ms:

                st.warning(
                    "The calling and receiving mobile stations "
                    "must be different."
                )

            else:

                with st.spinner("Establishing GSM call..."):

                    result = GSM.trace_call(
                        network,
                        source_ms,
                        destination_ms
                    )

                st.session_state["gsm_network"] = network

                st.session_state["last_gsm_call"] = result

        if "last_gsm_call" in st.session_state:

            result = st.session_state["last_gsm_call"]

            st.divider()

            st.subheader("Call Establishment Results")

            if result["status"] == "Success":

                st.success("Call successfully established!")

                col1, col2 = st.columns(2)

                col1.metric(
                    "Call ID",
                    result["call_id"]
                )

                col2.metric(
                    "Call Status",
                    result["status"]
                )

                st.write("Calling Station:", result["source"])

                st.write("Receiving Station:", result["destination"])

                st.write("Allocated BTS:", result["allocated_bts"])

                st.subheader("Call Routing Path")

                for step, component in enumerate(
                    result["route"],
                    start=1
                ):

                    st.write(f"{step}. {component}")

                st.info(result["message"])

            else:

                st.error(
                    result.get(
                        "reason",
                        "Call establishment failed."
                    )
                )

    # --------------------------------------------------------
    # PAGE 4: EXTERNAL CALL
    # --------------------------------------------------------

    elif architecture_page == "External Call":

        st.subheader("GSM External Network Call")

        st.write(
            "Simulate a call from a GSM mobile subscriber "
            "to an external telephone network."
        )

        mobile_stations = list(network["MS"].keys())

        source_ms = st.selectbox(
            "Select Calling Mobile Station",
            mobile_stations,
            key="external_source"
        )

        if st.button("📞 ESTABLISH EXTERNAL CALL"):

            with st.spinner("Routing external call..."):

                result = GSM.trace_external_call(
                    network,
                    source_ms
                )

            st.session_state["gsm_network"] = network

            st.session_state["last_external_call"] = result

        if "last_external_call" in st.session_state:

            result = st.session_state["last_external_call"]

            st.divider()

            if result["status"] == "Success":

                st.success("External call established!")

                st.metric(
                    "Call ID",
                    result["call_id"]
                )

                st.write(
                    "Calling Station:",
                    result["source"]
                )

                st.write(
                    "Destination:",
                    result["destination"]
                )

                st.subheader("External Call Routing")

                for step, component in enumerate(
                    result["route"],
                    start=1
                ):

                    st.write(f"{step}. {component}")

                st.info(result["message"])

            else:

                st.error(
                    result.get(
                        "reason",
                        "External call failed."
                    )
                )

    # --------------------------------------------------------
    # PAGE 5: CHANNEL MONITORING
    # --------------------------------------------------------

    elif architecture_page == "Channel Monitoring":

        st.subheader("BTS Radio Channel Monitoring")

        st.write(
            "Monitor the availability and utilization "
            "of radio channels at each BTS."
        )

        channel_data = GSM.get_channel_status(network)

        records = []

        for bts_id, details in channel_data.items():

            records.append({

                "BTS": bts_id,

                "Total Channels": details["total_channels"],

                "Occupied Channels": details["occupied_channels"],

                "Available Channels": details["available_channels"],

                "Utilization (%)": details["utilization_percent"],

                "Status": details["status"]

            })

        channel_df = pd.DataFrame(records)

        display_dataframe(channel_df)

        st.divider()

        st.subheader("Channel Utilization Graph")

        if not channel_df.empty:

            graph_data = channel_df.set_index("BTS")[
                ["Occupied Channels", "Available Channels"]
            ]

            st.bar_chart(graph_data)

        st.divider()

        st.subheader("Overall Channel Utilization")

        total_channels = sum(
            item["total_channels"]
            for item in channel_data.values()
        )

        occupied_channels = sum(
            item["occupied_channels"]
            for item in channel_data.values()
        )

        if total_channels > 0:

            utilization = (
                occupied_channels / total_channels
            ) * 100

        else:

            utilization = 0

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Channels",
            total_channels
        )

        col2.metric(
            "Occupied Channels",
            occupied_channels
        )

        col3.metric(
            "Overall Utilization",
            f"{utilization:.2f}%"
        )

        st.progress(
            min(utilization / 100, 1.0)
        )

    # --------------------------------------------------------
    # PAGE 6: ACTIVE CALLS
    # --------------------------------------------------------

    elif architecture_page == "Active Calls":

        st.subheader("Active GSM Calls")

        active_calls = GSM.get_active_calls(network)

        if active_calls:

            st.success(
                f"{len(active_calls)} active call(s) currently established."
            )

            records = []

            for call_id, details in active_calls.items():

                records.append({

                    "Call ID": call_id,

                    "Source": details["source"],

                    "Destination": details["destination"],

                    "Route": " → ".join(
                        map(str, details["route"])
                    ),

                    "Allocated BTS": ", ".join(
                        map(str, details["bts_list"])
                    )

                })

            active_df = pd.DataFrame(records)

            display_dataframe(active_df)

            st.divider()

            st.subheader("Terminate a Call")

            selected_call = st.selectbox(
                "Select Call ID",
                list(active_calls.keys())
            )

            if st.button("📴 TERMINATE SELECTED CALL"):

                result = GSM.terminate_call(
                    network,
                    selected_call
                )

                st.session_state["gsm_network"] = network

                if result["status"] == "Success":

                    st.success(
                        f"Call {selected_call} terminated successfully."
                    )

                    st.info(
                        "The allocated BTS radio channels "
                        "have been released."
                    )

                else:

                    st.error(
                        result.get(
                            "reason",
                            "Call termination failed."
                        )
                    )

                st.rerun()

        else:

            st.info(
                "There are currently no active GSM calls. "
                "Establish a mobile-to-mobile or external call "
                "to see it here."
            )

    st.divider()

    st.caption(
        "GSM Architecture and Call Routing Simulation Module"
    )

# ============================================================
# 8. NETWORK BENCHMARKING MODULE
# ============================================================

elif selected_module == "Network Benchmarking":

    st.header("📊 NETWORK BENCHMARKING")

    st.caption(
        "End-to-end network performance measurement and analysis."
    )

    benchmark_page = st.sidebar.radio(
        "BENCHMARKING MENU",
        [
            "Live Ping Test",
            "Wireshark Analysis",
            "Performance Comparison"
        ],
        key="benchmark_navigation"
    )

    st.divider()


    # --------------------------------------------------------
    # PAGE 1: LIVE PING TEST
    # --------------------------------------------------------

    if benchmark_page == "Live Ping Test":

        st.subheader("1. Live Network Benchmarking")

        st.write(
            "Test connectivity and measure round-trip time "
            "between your computer and a destination."
        )

        col1, col2 = st.columns(2)

        with col1:

            destination = st.text_input(
                "Destination IP or hostname",
                "8.8.8.8"
            )

        with col2:

            ping_count = st.number_input(
                "Number of Ping Packets",
                min_value=1,
                max_value=100,
                value=20
            )

        if st.button("🚀 RUN LIVE NETWORK TEST"):

            with st.spinner("Testing network performance..."):

                try:

                    ping_results = Network.analyze_ping(
                        destination=destination,
                        count=int(ping_count)
                    )

                    st.session_state["ping_results"] = ping_results

                    st.success("Network test completed!")

                except Exception as e:

                    st.error(f"Ping test failed: {e}")

        if "ping_results" in st.session_state:

            results = st.session_state["ping_results"]

            st.divider()

            st.subheader("Live Ping Results")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Average Latency",
                safe_metric(results.get("average_latency"), " ms")
            )

            col2.metric(
                "Jitter",
                safe_metric(results.get("jitter"), " ms")
            )

            col3.metric(
                "Packet Loss",
                safe_metric(results.get("packet_loss"), "%")
            )

            col4.metric(
                "Packets Received",
                results.get("received", 0)
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Packets Sent",
                results.get("sent", 0)
            )

            col2.metric(
                "Minimum Latency",
                safe_metric(results.get("minimum_latency"), " ms")
            )

            col3.metric(
                "Maximum Latency",
                safe_metric(results.get("maximum_latency"), " ms")
            )

            rtt_values = results.get("rtt_values", [])

            if rtt_values:

                st.subheader("Latency Variation")

                fig, ax = plt.subplots(figsize=(10, 4))

                ax.plot(
                    range(1, len(rtt_values) + 1),
                    rtt_values,
                    marker="o"
                )

                ax.set_title("Live Ping Latency Variation")
                ax.set_xlabel("Ping Number")
                ax.set_ylabel("Round Trip Time (ms)")
                ax.grid(True)

                st.pyplot(fig)

                plt.close(fig)

            else:

                st.warning("No ping replies were received.")


    # --------------------------------------------------------
    # PAGE 2: WIRESHARK ANALYSIS
    # --------------------------------------------------------

    elif benchmark_page == "Wireshark Analysis":

        st.subheader("2. Wireshark Packet Analysis")

        st.write(
            "Upload a Wireshark packet capture file "
            "(.pcap or .pcapng) for analysis."
        )

        uploaded_file = st.file_uploader(
            "Upload Wireshark Capture",
            type=["pcap", "pcapng"]
        )

        if uploaded_file is not None:

            if st.button("🔍 ANALYZE PACKET CAPTURE"):

                try:

                    with st.spinner("Analyzing packet capture..."):

                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".pcapng"
                        ) as temp_file:

                            temp_file.write(uploaded_file.getvalue())

                            temp_path = temp_file.name

                        try:

                            df, capture_results = Network.analyze_capture(
                                temp_path
                            )

                            st.session_state["capture_df"] = df

                            st.session_state["capture_results"] = (
                                capture_results
                            )

                            st.success(
                                "Packet capture analyzed successfully!"
                            )

                        finally:

                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                except Exception as e:

                    st.error(f"Packet analysis failed: {e}")

        if "capture_results" in st.session_state:

            capture_results = st.session_state["capture_results"]

            df = st.session_state["capture_df"]

            st.divider()

            st.subheader("Packet Statistics")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Packets",
                f"{capture_results['total_packets']:,}"
            )

            col2.metric(
                "TCP Packets",
                f"{capture_results['tcp_count']:,}"
            )

            col3.metric(
                "UDP Packets",
                f"{capture_results['udp_count']:,}"
            )

            col4.metric(
                "ICMP Packets",
                f"{capture_results['icmp_count']:,}"
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Traffic",
                f"{capture_results['total_bytes'] / 1024:.2f} KB"
            )

            col2.metric(
                "Average Packet Size",
                safe_metric(
                    capture_results["average_packet_size"],
                    " bytes"
                )
            )

            st.divider()

            st.subheader("Captured Network Performance")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Average Latency",
                safe_metric(
                    capture_results["average_latency"],
                    " ms"
                )
            )

            col2.metric(
                "Jitter",
                safe_metric(
                    capture_results["jitter"],
                    " ms"
                )
            )

            col3.metric(
                "Packet Loss",
                safe_metric(
                    capture_results["packet_loss"],
                    "%"
                )
            )

            col4.metric(
                "Captured Throughput",
                safe_metric(
                    capture_results["throughput_mbps"],
                    " Mbps"
                )
            )

            st.divider()

            st.subheader("Protocol Distribution")

            if not df.empty and "Protocol" in df.columns:

                protocol_counts = df["Protocol"].value_counts()

                fig, ax = plt.subplots(figsize=(8, 4))

                ax.pie(
                    protocol_counts.values,
                    labels=protocol_counts.index,
                    autopct="%1.1f%%"
                )

                ax.set_title("Network Protocol Distribution")

                st.pyplot(fig)

                plt.close(fig)

            st.divider()

            st.subheader("Packet Size Distribution")

            if not df.empty and "Size" in df.columns:

                fig, ax = plt.subplots(figsize=(9, 4))

                ax.hist(
                    df["Size"],
                    bins=30
                )

                ax.set_xlabel("Packet Size (bytes)")
                ax.set_ylabel("Number of Packets")
                ax.set_title("Packet Size Analysis")

                st.pyplot(fig)

                plt.close(fig)

            st.divider()

            st.subheader("Captured Packet Records")

            display_dataframe(df.head(100))

            st.download_button(
                "⬇️ DOWNLOAD PACKET ANALYSIS CSV",
                df.to_csv(index=False),
                "packet_analysis.csv",
                "text/csv"
            )


    # --------------------------------------------------------
    # PAGE 3: PERFORMANCE COMPARISON
    # --------------------------------------------------------

    elif benchmark_page == "Performance Comparison":

        st.subheader("3. Network Benchmarking Comparison")

        if (
            "ping_results" in st.session_state
            and "capture_results" in st.session_state
        ):

            ping = st.session_state["ping_results"]

            capture = st.session_state["capture_results"]

            comparison = pd.DataFrame({

                "Performance Parameter": [
                    "Average Latency (ms)",
                    "Jitter (ms)",
                    "Packet Loss (%)"
                ],

                "Live Ping": [
                    ping["average_latency"],
                    ping["jitter"],
                    ping["packet_loss"]
                ],

                "Wireshark": [
                    capture["average_latency"],
                    capture["jitter"],
                    capture["packet_loss"]
                ]

            })

            display_dataframe(comparison)

            st.bar_chart(
                comparison.set_index("Performance Parameter")
            )

            st.info(
                "For a valid comparison, the Wireshark capture should "
                "contain the same ping test, including its requests "
                "and replies. Otherwise, the measurements represent "
                "different test periods."
            )

        else:

            st.warning(
                "First run a Live Ping Test and analyze a Wireshark "
                "capture. Their results will then appear here."
            )


# ============================================================
# 9. GSM TRAFFIC SIMULATION MODULE
# ============================================================

elif selected_module == "GSM Traffic Simulation":

    st.header("📞 GSM CELLULAR TELE-TRAFFIC SYSTEM")

    st.caption(
        "Mathematical Modelling and Simulation of GSM Call Traffic"
    )

    traffic_page = st.sidebar.radio(
        "TRAFFIC SIMULATION MENU",
        [
            "M/M/1 Model",
            "M/M/S Model",
            "Erlang B and C",
            "SimPy Call Simulation",
            "Model Comparison"
        ],
        key="traffic_navigation"
    )

    st.divider()


    # --------------------------------------------------------
    # PAGE 1: M/M/1 MODEL
    # --------------------------------------------------------

    if traffic_page == "M/M/1 Model":

        st.subheader("A. M/M/1 Queuing Model")

        st.write(
            "This model represents a single-server system "
            "where calls arrive randomly and are served one at a time."
        )

        col1, col2 = st.columns(2)

        with col1:

            arrival_rate = st.number_input(
                "Call Arrival Rate (calls/minute)",
                min_value=0.0,
                value=8.0,
                step=1.0,
                key="mm1_arrival"
            )

        with col2:

            service_rate = st.number_input(
                "Service Rate (calls/minute)",
                min_value=0.1,
                value=10.0,
                step=1.0,
                key="mm1_service"
            )

        if st.button("RUN M/M/1 ANALYSIS"):

            try:

                result = Traffic.mm1_model(
                    arrival_rate,
                    service_rate
                )

                st.session_state["mm1_result"] = result

            except Exception as e:

                st.error(f"Model calculation failed: {e}")

        if "mm1_result" in st.session_state:

            mm1 = st.session_state["mm1_result"]

            if mm1["stable"]:

                st.divider()

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Channel Utilization",
                    f"{mm1['utilization'] * 100:.2f}%"
                )

                col2.metric(
                    "Average Queue Length",
                    f"{mm1['Lq']:.4f} calls"
                )

                col3.metric(
                    "Average Waiting Time",
                    f"{mm1['Wq'] * 60:.4f} seconds"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Average Calls in System",
                    f"{mm1['L']:.4f}"
                )

                col2.metric(
                    "Average Time in System",
                    f"{mm1['W'] * 60:.4f} seconds"
                )

                col3.metric(
                    "System Capacity",
                    f"{mm1['capacity']:.2f} calls/min"
                )

                st.success("M/M/1 model is stable.")

            else:

                st.error(mm1["message"])


    # --------------------------------------------------------
    # PAGE 2: M/M/S MODEL
    # --------------------------------------------------------

    elif traffic_page == "M/M/S Model":

        st.subheader("B. M/M/S Queuing Model")

        st.write(
            "This model represents a GSM base station "
            "with multiple channels serving incoming calls."
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            arrival_rate = st.number_input(
                "Call Arrival Rate (calls/minute)",
                min_value=0.0,
                value=8.0,
                key="mms_arrival"
            )

        with col2:

            service_rate = st.number_input(
                "Service Rate per Channel",
                min_value=0.1,
                value=10.0,
                key="mms_service"
            )

        with col3:

            servers = st.number_input(
                "Number of BTS Channels",
                min_value=1,
                max_value=100,
                value=5,
                key="mms_servers"
            )

        if st.button("RUN M/M/S ANALYSIS"):

            try:

                result = Traffic.mms_model(
                    arrival_rate,
                    service_rate,
                    int(servers)
                )

                st.session_state["mms_result"] = result

            except Exception as e:

                st.error(f"Model calculation failed: {e}")

        if "mms_result" in st.session_state:

            mms = st.session_state["mms_result"]

            if mms["stable"]:

                st.divider()

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Channel Utilization",
                    f"{mms['utilization'] * 100:.2f}%"
                )

                col2.metric(
                    "Average Queue Length",
                    f"{mms['Lq']:.4f} calls"
                )

                col3.metric(
                    "Average Waiting Time",
                    f"{mms['Wq'] * 60:.4f} seconds"
                )

                col4.metric(
                    "Probability of Waiting",
                    f"{mms['P_wait'] * 100:.4f}%"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Average Calls in System",
                    f"{mms['L']:.4f}"
                )

                col2.metric(
                    "Average Time in System",
                    f"{mms['W'] * 60:.4f} seconds"
                )

                col3.metric(
                    "Total BTS Capacity",
                    f"{mms['capacity']:.2f} calls/min"
                )

                st.success("M/M/S model is stable.")

            else:

                st.error(mms["message"])


    # --------------------------------------------------------
    # PAGE 3: ERLANG B AND C
    # --------------------------------------------------------

    elif traffic_page == "Erlang B and C":

        st.subheader("C. Erlang B and Erlang C Traffic Models")

        st.write(
            "Erlang B estimates call blocking in a system "
            "without a waiting queue. Erlang C estimates "
            "the probability of waiting in a queued system."
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            arrival_rate = st.number_input(
                "Call Arrival Rate (calls/minute)",
                min_value=0.1,
                value=8.0,
                key="erlang_arrival"
            )

        with col2:

            service_rate = st.number_input(
                "Service Rate per Channel",
                min_value=0.1,
                value=10.0,
                key="erlang_service"
            )

        with col3:

            channels = st.number_input(
                "Number of Channels",
                min_value=1,
                max_value=100,
                value=5,
                key="erlang_channels"
            )

        if st.button("RUN ERLANG ANALYSIS"):

            try:

                eb = Traffic.erlang_b(
                    arrival_rate,
                    service_rate,
                    int(channels)
                )

                ec = Traffic.erlang_c(
                    arrival_rate,
                    service_rate,
                    int(channels)
                )

                if isinstance(ec, dict):

                    ec_probability = ec["P_wait"]

                else:

                    ec_probability = ec

                st.session_state["erlang_b_result"] = eb

                st.session_state["erlang_c_result"] = ec_probability

            except Exception as e:

                st.error(f"Erlang calculation failed: {e}")

        if "erlang_b_result" in st.session_state:

            eb = st.session_state["erlang_b_result"]

            ec = st.session_state["erlang_c_result"]

            st.divider()

            col1, col2 = st.columns(2)

            col1.metric(
                "Erlang B Blocking Probability",
                f"{eb * 100:.4f}%"
            )

            col2.metric(
                "Erlang C Waiting Probability",
                f"{ec * 100:.4f}%"
            )

            st.subheader("Interpretation")

            st.write(
                f"The Erlang B model predicts a call blocking "
                f"probability of {eb * 100:.4f}%."
            )

            st.write(
                f"The Erlang C model predicts a waiting "
                f"probability of {ec * 100:.4f}%."
            )


    # --------------------------------------------------------
    # PAGE 4: SIMPY CALL SIMULATION
    # --------------------------------------------------------

    elif traffic_page == "SimPy Call Simulation":

        st.subheader("D. GSM Call Traffic Simulation")

        st.write(
            "Simulate individual calls arriving at a GSM base station. "
            "Observe successful calls, blocked calls, waiting time "
            "and channel utilization."
        )

        col1, col2 = st.columns(2)

        with col1:

            arrival_rate = st.number_input(
                "Call Arrival Rate (calls/minute)",
                min_value=0.1,
                value=8.0,
                key="sim_arrival"
            )

            service_rate = st.number_input(
                "Service Rate per Channel",
                min_value=0.1,
                value=10.0,
                key="sim_service"
            )

        with col2:

            channels = st.number_input(
                "Available BTS Channels",
                min_value=1,
                max_value=100,
                value=5,
                key="sim_channels"
            )

            total_calls = st.number_input(
                "Number of Calls to Simulate",
                min_value=100,
                max_value=100000,
                value=10000,
                step=100,
                key="sim_calls"
            )

        simulation_mode = st.selectbox(
            "Simulation Mode",
            [
                "queue",
                "blocking"
            ],
            format_func=lambda x: (
                "Calls Wait in Queue"
                if x == "queue"
                else "Calls Blocked When Channels Are Full"
            )
        )

        if st.button("🚀 RUN GSM SIMULATION"):

            try:

                with st.spinner(
                    "Simulating GSM call traffic..."
                ):

                    results = Traffic.gsm_call_simulation(
                        arrival_rate=arrival_rate,
                        service_rate=service_rate,
                        channels=int(channels),
                        total_calls=int(total_calls),
                        simulation_mode=simulation_mode
                    )

                st.session_state["simulation_results"] = results

                st.success("Simulation completed!")

            except Exception as e:

                st.error(f"Simulation failed: {e}")

        if "simulation_results" in st.session_state:

            results = st.session_state["simulation_results"]

            st.divider()

            st.subheader("Simulation Results")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Generated Calls",
                results["generated"]
            )

            col2.metric(
                "Successful Calls",
                results["successful"]
            )

            col3.metric(
                "Blocked Calls",
                results["blocked"]
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Blocking Probability",
                f"{results['blocking_probability_percent']:.3f}%"
            )

            col2.metric(
                "Average Waiting Time",
                f"{results['average_wait_seconds']:.3f} seconds"
            )

            col3.metric(
                "Channel Utilization",
                f"{results['channel_utilization_percent']:.2f}%"
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Average Call Duration",
                f"{results['average_call_duration_seconds']:.2f} seconds"
            )

            col2.metric(
                "Simulation Duration",
                f"{results['simulation_time_minutes']:.2f} minutes"
            )

            st.divider()

            st.subheader("Simulation Summary")

            summary = pd.DataFrame({

                "Parameter": [
                    "Generated Calls",
                    "Successful Calls",
                    "Blocked Calls",
                    "Blocking Probability (%)",
                    "Average Waiting Time (seconds)",
                    "Average Call Duration (seconds)",
                    "Channel Utilization (%)"
                ],

                "Result": [
                    results["generated"],
                    results["successful"],
                    results["blocked"],
                    results["blocking_probability_percent"],
                    results["average_wait_seconds"],
                    results["average_call_duration_seconds"],
                    results["channel_utilization_percent"]
                ]

            })

            display_dataframe(summary)

            st.download_button(
                "⬇️ DOWNLOAD SIMULATION RESULTS",
                summary.to_csv(index=False),
                "gsm_simulation_results.csv",
                "text/csv"
            )


    # --------------------------------------------------------
    # PAGE 5: MODEL COMPARISON
    # --------------------------------------------------------

    elif traffic_page == "Model Comparison":

        st.subheader("E. M/M/1 versus M/M/S Comparison")

        st.write(
            "Compare the theoretical performance of a single-channel "
            "system with a multiple-channel GSM system."
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            arrival_rate = st.number_input(
                "Arrival Rate (calls/minute)",
                min_value=0.1,
                value=8.0,
                key="compare_arrival"
            )

        with col2:

            service_rate = st.number_input(
                "Service Rate per Channel",
                min_value=0.1,
                value=10.0,
                key="compare_service"
            )

        with col3:

            servers = st.number_input(
                "Number of Channels",
                min_value=2,
                max_value=100,
                value=5,
                key="compare_servers"
            )

        if st.button("COMPARE QUEUING MODELS"):

            try:

                mm1 = Traffic.mm1_model(
                    arrival_rate,
                    service_rate
                )

                mms = Traffic.mms_model(
                    arrival_rate,
                    service_rate,
                    int(servers)
                )

                st.session_state["comparison_mm1"] = mm1

                st.session_state["comparison_mms"] = mms

            except Exception as e:

                st.error(f"Comparison failed: {e}")

        if (
            "comparison_mm1" in st.session_state
            and "comparison_mms" in st.session_state
        ):

            mm1 = st.session_state["comparison_mm1"]

            mms = st.session_state["comparison_mms"]

            if mm1["stable"] and mms["stable"]:

                comparison = pd.DataFrame({

                    "Performance Parameter": [
                        "Channel Utilization (%)",
                        "Average Queue Length",
                        "Average Waiting Time (seconds)",
                        "Average Time in System (seconds)",
                        "System Capacity (calls/minute)"
                    ],

                    "M/M/1": [
                        mm1["utilization"] * 100,
                        mm1["Lq"],
                        mm1["Wq"] * 60,
                        mm1["W"] * 60,
                        mm1["capacity"]
                    ],

                    "M/M/S": [
                        mms["utilization"] * 100,
                        mms["Lq"],
                        mms["Wq"] * 60,
                        mms["W"] * 60,
                        mms["capacity"]
                    ]

                })

                st.divider()

                display_dataframe(comparison)

                st.subheader("Performance Comparison Graph")

                graph_data = comparison.set_index(
                    "Performance Parameter"
                )

                st.bar_chart(graph_data)

            else:

                st.warning(
                    "Both models must be stable before comparison."
                )


# ============================================================
# 10. INSTALLATION AND MAINTENANCE MODULE
# ============================================================

elif selected_module == "Installation and Maintenance":

    st.header("🏗️ GSM BASE STATION INSTALLATION AND MAINTENANCE")

    st.caption(
        "Equipment Registration, Installation Management "
        "and Preventive Maintenance"
    )

    installation_page = st.sidebar.radio(
        "INSTALLATION AND MAINTENANCE MENU",
        [
            "Overview",
            "Equipment Registration",
            "Installation Checklist",
            "Preventive Maintenance",
            "Inspection and Fault Reports"
        ],
        key="installation_navigation"
    )

    st.divider()


    # --------------------------------------------------------
    # PAGE 1: OVERVIEW
    # --------------------------------------------------------

    if installation_page == "Overview":

        st.subheader("Installation and Maintenance Overview")

        total_equipment = len(equipment)

        installed = (
            len(equipment[equipment["Status"] == "Installed"])
            if not equipment.empty else 0
        )

        pending = (
            len(equipment[equipment["Status"] == "Pending"])
            if not equipment.empty else 0
        )

        overdue = 0

        if not maintenance.empty:

            dates = pd.to_datetime(
                maintenance["Scheduled Date"],
                errors="coerce"
            )

            overdue = len(
                maintenance[
                    (maintenance["Status"] == "Pending") &
                    (dates < pd.Timestamp(date.today()))
                ]
            )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Equipment", total_equipment)

        col2.metric("Installed Equipment", installed)

        col3.metric("Pending Installation", pending)

        col4.metric("Overdue Maintenance", overdue)

        st.divider()

        st.subheader("Equipment Installation Status")

        if not equipment.empty:

            st.bar_chart(
                equipment["Status"].value_counts()
            )

            display_dataframe(equipment)

        else:

            st.info("No equipment has been registered.")

        st.divider()

        st.subheader("Maintenance Alerts")

        if not maintenance.empty:

            pending_maintenance = maintenance[
                maintenance["Status"] == "Pending"
            ].copy()

            pending_dates = pd.to_datetime(
                pending_maintenance["Scheduled Date"],
                errors="coerce"
            )

            overdue_records = pending_maintenance[
                pending_dates < pd.Timestamp(date.today())
            ]

            upcoming_records = pending_maintenance[
                pending_dates >= pd.Timestamp(date.today())
            ]

            if not overdue_records.empty:

                st.error(
                    f"{len(overdue_records)} maintenance records "
                    "are overdue."
                )

                display_dataframe(overdue_records)

            if not upcoming_records.empty:

                st.info("Upcoming Maintenance")

                display_dataframe(
                    upcoming_records.sort_values("Scheduled Date")
                )

            if pending_maintenance.empty:

                st.success("No pending maintenance activities.")

        else:

            st.info("No maintenance schedules available.")


    # --------------------------------------------------------
    # PAGE 2: EQUIPMENT REGISTRATION
    # --------------------------------------------------------

    elif installation_page == "Equipment Registration":

        st.subheader("Equipment Registration")

        with st.form("equipment_form"):

            equipment_name = st.selectbox(
                "Equipment Name",
                [
                    "BTS Cabinet",
                    "Radio Unit",
                    "Antenna",
                    "Feeder Cable",
                    "Transmission Equipment",
                    "Rectifier",
                    "Backup Battery",
                    "Earthing System",
                    "Cooling System",
                    "Other"
                ]
            )

            category = st.selectbox(
                "Equipment Category",
                [
                    "Radio Equipment",
                    "Transmission Equipment",
                    "Power Equipment",
                    "Antenna System",
                    "Protection Equipment",
                    "Environmental Equipment",
                    "Other"
                ]
            )

            location = st.text_input(
                "Installation Location"
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                step=1
            )

            installation_date = st.date_input(
                "Installation Date",
                value=date.today()
            )

            status = st.selectbox(
                "Installation Status",
                ["Pending", "Installed"]
            )

            submit = st.form_submit_button(
                "REGISTER EQUIPMENT"
            )

            if submit:

                if not location.strip():

                    st.error("Enter the installation location.")

                else:

                    new_equipment = {

                        "Equipment ID": str(uuid.uuid4())[:8].upper(),

                        "Equipment Name": equipment_name,

                        "Category": category,

                        "Location": location,

                        "Quantity": quantity,

                        "Installation Date": str(installation_date),

                        "Status": status

                    }

                    equipment = pd.concat(
                        [
                            equipment,
                            pd.DataFrame([new_equipment])
                        ],
                        ignore_index=True
                    )

                    save_csv(
                        equipment,
                        EQUIPMENT_FILE
                    )

                    st.success(
                        "Equipment registered successfully!"
                    )

        st.divider()

        st.subheader("Registered Equipment")

        display_dataframe(equipment)


    # --------------------------------------------------------
    # PAGE 3: INSTALLATION CHECKLIST
    # --------------------------------------------------------

    elif installation_page == "Installation Checklist":

        st.subheader("GSM Installation Checklist")

        activities = [

            "Site survey completed",

            "Site preparation completed",

            "Tower foundation inspected",

            "Tower structure erected",

            "Antennas installed and aligned",

            "BTS cabinet installed",

            "Transmission equipment installed",

            "Power supply installed",

            "Backup batteries installed",

            "Earthing system connected",

            "Feeder cables connected",

            "Cable connections inspected",

            "Cooling system checked",

            "Equipment powered up",

            "Commissioning tests completed",

            "Acceptance testing completed"

        ]

        if not equipment.empty:

            with st.form("checklist_form"):

                selected_id = st.selectbox(
                    "Select Equipment ID",
                    equipment["Equipment ID"].tolist()
                )

                activity = st.selectbox(
                    "Installation Activity",
                    activities
                )

                activity_status = st.selectbox(
                    "Activity Status",
                    ["Pending", "In Progress", "Completed"]
                )

                remarks = st.text_area(
                    "Engineer Remarks"
                )

                submit = st.form_submit_button(
                    "SAVE INSTALLATION RECORD"
                )

                if submit:

                    record = {

                        "Equipment ID": selected_id,

                        "Activity": activity,

                        "Status": activity_status,

                        "Remarks": remarks,

                        "Date": str(date.today())

                    }

                    checklist = pd.concat(
                        [
                            checklist,
                            pd.DataFrame([record])
                        ],
                        ignore_index=True
                    )

                    save_csv(
                        checklist,
                        CHECKLIST_FILE
                    )

                    st.success(
                        "Installation record saved!"
                    )

            st.divider()

            st.subheader("Installation Records")

            display_dataframe(checklist)

            if not checklist.empty:

                completed = len(
                    checklist[
                        checklist["Status"] == "Completed"
                    ]
                )

                total = len(checklist)

                progress = completed / total

                st.subheader("Installation Progress")

                st.progress(progress)

                st.write(
                    f"{completed} of {total} recorded activities completed."
                )

        else:

            st.warning(
                "Register equipment before recording installation activities."
            )


    # --------------------------------------------------------
    # PAGE 4: PREVENTIVE MAINTENANCE
    # --------------------------------------------------------

    elif installation_page == "Preventive Maintenance":

        st.subheader("Preventive Maintenance Management")

        if not equipment.empty:

            with st.form("maintenance_form"):

                selected_id = st.selectbox(
                    "Select Equipment",
                    equipment["Equipment ID"].tolist()
                )

                selected_row = equipment[
                    equipment["Equipment ID"] == selected_id
                ].iloc[0]

                st.write(
                    "Equipment:",
                    selected_row["Equipment Name"]
                )

                activity = st.selectbox(
                    "Maintenance Activity",
                    [
                        "Visual equipment inspection",
                        "Antenna alignment inspection",
                        "Feeder cable inspection",
                        "Battery condition inspection",
                        "Rectifier voltage testing",
                        "Earthing system inspection",
                        "Cooling system cleaning",
                        "BTS alarm inspection",
                        "Transmission link inspection",
                        "General equipment servicing"
                    ]
                )

                scheduled_date = st.date_input(
                    "Next Maintenance Date",
                    value=date.today() + timedelta(days=30)
                )

                frequency = st.selectbox(
                    "Maintenance Frequency",
                    [
                        "Weekly",
                        "Monthly",
                        "Quarterly",
                        "Biannually",
                        "Annually"
                    ]
                )

                submit = st.form_submit_button(
                    "SAVE MAINTENANCE SCHEDULE"
                )

                if submit:

                    schedule = {

                        "Maintenance ID": str(uuid.uuid4())[:8].upper(),

                        "Equipment ID": selected_id,

                        "Equipment Name": selected_row["Equipment Name"],

                        "Maintenance Activity": activity,

                        "Scheduled Date": str(scheduled_date),

                        "Frequency": frequency,

                        "Status": "Pending"

                    }

                    maintenance = pd.concat(
                        [
                            maintenance,
                            pd.DataFrame([schedule])
                        ],
                        ignore_index=True
                    )

                    save_csv(
                        maintenance,
                        MAINTENANCE_FILE
                    )

                    st.success(
                        "Maintenance schedule created!"
                    )

            st.divider()

            st.subheader("Maintenance Records")

            display_dataframe(maintenance)

            if not maintenance.empty:

                schedule_id = st.selectbox(
                    "Select Maintenance Record",
                    maintenance["Maintenance ID"].tolist()
                )

                new_status = st.selectbox(
                    "Update Maintenance Status",
                    ["Pending", "Completed"]
                )

                if st.button("UPDATE MAINTENANCE"):

                    maintenance.loc[
                        maintenance["Maintenance ID"] == schedule_id,
                        "Status"
                    ] = new_status

                    save_csv(
                        maintenance,
                        MAINTENANCE_FILE
                    )

                    st.success(
                        "Maintenance status updated!"
                    )

        else:

            st.warning(
                "Register equipment before creating maintenance schedules."
            )


    # --------------------------------------------------------
    # PAGE 5: INSPECTION AND FAULT REPORTS
    # --------------------------------------------------------

    elif installation_page == "Inspection and Fault Reports":

        st.subheader("Equipment Inspection and Fault Reporting")

        if not equipment.empty:

            with st.form("inspection_form"):

                selected_id = st.selectbox(
                    "Select Equipment",
                    equipment["Equipment ID"].tolist()
                )

                selected_row = equipment[
                    equipment["Equipment ID"] == selected_id
                ].iloc[0]

                inspection_date = st.date_input(
                    "Inspection Date",
                    value=date.today()
                )

                condition = st.selectbox(
                    "Equipment Condition",
                    ["Good", "Fair", "Poor", "Faulty"]
                )

                fault = st.text_area(
                    "Fault Description"
                )

                corrective_action = st.text_area(
                    "Corrective Action"
                )

                submit = st.form_submit_button(
                    "SAVE INSPECTION REPORT"
                )

                if submit:

                    report = {

                        "Inspection ID": str(uuid.uuid4())[:8].upper(),

                        "Equipment ID": selected_id,

                        "Equipment Name": selected_row["Equipment Name"],

                        "Inspection Date": str(inspection_date),

                        "Condition": condition,

                        "Fault Description": fault,

                        "Corrective Action": corrective_action

                    }

                    inspections = pd.concat(
                        [
                            inspections,
                            pd.DataFrame([report])
                        ],
                        ignore_index=True
                    )

                    save_csv(
                        inspections,
                        INSPECTION_FILE
                    )

                    st.success(
                        "Inspection report saved!"
                    )

            st.divider()

            st.subheader("Inspection History")

            display_dataframe(inspections)

            st.divider()

            st.subheader("Fault Reports")

            faulty_records = inspections[
                inspections["Condition"].isin(["Poor", "Faulty"])
            ]

            if not faulty_records.empty:

                st.error(
                    f"{len(faulty_records)} equipment inspection(s) "
                    "require attention."
                )

                display_dataframe(faulty_records)

            else:

                st.success("No faulty equipment has been reported.")

        else:

            st.warning(
                "Register equipment before recording inspection reports."
            )


# ============================================================
# 11. FOOTER
# ============================================================

st.divider()

st.caption(
    "GSM Telecommunications Network Monitoring and Simulation System | "
    "Network Benchmarking • Traffic Engineering • BTS Management"
)