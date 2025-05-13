def format_metrics(current: dict, history: dict) -> str:
    def fmt_gb(val): return f"{val / (1024 ** 3):.1f} GB"
    def fmt_kbps(val): return f"{val * 8 / 1024:.0f} Kbps"
    def fmt_percent(val): return f"{val:.1f}%"
    def fmt_stat(hist: dict, suffix="") -> str:
        if hist:
            return f" (avg: {hist.get('avg', 0):.1f}{suffix}, max: {hist.get('max', 0):.1f}{suffix})"
        return ""

    text = ""

    if "CPU" in current:
        cpu = current["CPU"]
        hist_cpu = history.get("CPU", {})
        user = cpu.get("User", 0)
        system = cpu.get("System", 0)
        total_active = user + system
        load1 = cpu.get("Load1", 0)
        text += f"📊 <b>CPU:</b> {fmt_percent(total_active)} (Load 1m: {load1:.2f})\n"
        text += f"├ User: {fmt_percent(user)}{fmt_stat(hist_cpu.get('User'), '%')}\n"
        text += f"├ System: {fmt_percent(system)}{fmt_stat(hist_cpu.get('System'), '%')}\n"
        if "Idle" in cpu:
            text += f"└ Idle: {fmt_percent(cpu['Idle'])}{fmt_stat(hist_cpu.get('Idle'), '%')}\n"

    if "Memory" in current:
        mem = current["Memory"]
        hist_mem = history.get("Memory", {})
        used = mem.get("Used_bytes", 0)
        available = mem.get("Available_bytes", 0)
        text += f"\n💾 <b>RAM:</b> {fmt_gb(used)} used / {fmt_gb(available)} available\n"
        if "Used" in hist_mem:
            text += f"├ Used avg: {hist_mem['Used']['avg']:.1f}%, max: {hist_mem['Used']['max']:.1f}%\n"

    if "Disk" in current:
        disk = current["Disk"]
        hist_disk = history.get("Disk", {})
        used = disk.get("Used_bytes", 0)
        total = disk.get("Total_bytes", 1)
        text += f"\n📀 <b>Disk:</b> {fmt_gb(used)} used / {fmt_gb(total)} total (/)\n"
        if "Used" in hist_disk:
            text += f"├ Used avg: {hist_disk['Used']['avg']:.1f}%, max: {hist_disk['Used']['max']:.1f}%\n"
        if "Read_bytes" in disk and "Write_bytes" in disk:
            read = disk["Read_bytes"]

            write = disk["Write_bytes"]
            text += f"└ I/O: ⬇ {fmt_kbps(read)} | ⬆ {fmt_kbps(write)}\n"

    if "Network" in current:
        net = current["Network"]
        sent = net.get("Bytes_sent", 0)
        recv = net.get("Bytes_recv", 0)
        text += f"\n🌐 <b>Network:</b> ↑ {fmt_kbps(sent)} | ↓ {fmt_kbps(recv)}"
        err_in = net.get("Err_in", 0)
        err_out = net.get("Err_out", 0)
        if err_in or err_out:
            text += f" | Errors: in {err_in} out {err_out}"
        text += "\n"

    return text.strip()




def get_emoji(value: float) -> str:
    if value < 60:
        return "🟢"
    elif value < 85:
        return "🟠"
    else:
        return "🔴"
