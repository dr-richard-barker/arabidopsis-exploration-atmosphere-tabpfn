"""
Figure 7 Generator: Plant PhysioSpace Stress Autodecoder Across the NASA Exploration Atmosphere Mission Profile.

Generates publication-grade 300 DPI Figure 7 adhering to Nature/Cell guidelines:
  - Panel A: Master Mission Profile Stress Autodecoder Heatmap (Blue-White-Red diverging palette)
  - Panel B: PhysioSpace 2D Ordination Trajectory (Hypoxia vs. Osmotic/Boundary-Layer Axes)
  - Panel C: Organ-Specific Stress Partitioning (Shoot vs. Root Divergence)
  - Panel D: Engineered BLiSS Relative Humidity Rescue Delta (M3 vs. M6)
"""
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
import seaborn as sns

WORKSPACE = Path("/Users/drb_laptop/Documents/Exploration_atmosphere_Biomni_lab_downloads_20261016_234156")
PROJECT_DIR = WORKSPACE / "arabidopsis_exploration_atmosphere"
FIG_DIR = PROJECT_DIR / "manuscript" / "figures"
DOCS_FIG_DIR = PROJECT_DIR / "docs" / "figures"
BRAIN_DIR = Path("/Users/drb_laptop/.gemini/antigravity/brain/4ccd0097-6c0d-4041-936a-b8412eaf0642")

from atmos_ml.physiospace import compute_mission_physiospace_scores, PHYSIOSPACE_DIMENSIONS, MISSION_PHASES

# Colorblind-safe, visually striking Blue-White-Red Diverging Colormap
# Low = Deep Blue (#2166ac) -> Baseline/Homeostasis = White (#ffffff) -> High = Deep Red (#b2182b)
BLUE_WHITE_RED_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "BlueWhiteRed",
    [
        (0.00, "#053061"), # Extreme low/suppressed
        (0.15, "#2166ac"), # Low
        (0.35, "#67a9cf"), # Moderate low
        (0.48, "#d1e5f0"), # Pale low
        (0.50, "#ffffff"), # Baseline / zero / homeostasis
        (0.52, "#fddbc7"), # Pale elevated
        (0.65, "#ef8a62"), # Moderate elevated
        (0.85, "#b2182b"), # High
        (1.00, "#67001f"), # Extreme high/hyperactivated
    ]
)

# Typography constants
FONT_FAMILY = "sans-serif"
plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["svg.fonttype"] = "none"


def _anchor_xticks(ax, rotation=38, ha="right", va="top", fontsize=8.5, weight="normal"):
    """Anchors rotated x-tick labels directly below tick marks."""
    labels = ax.get_xticklabels()
    for lbl in labels:
        lbl.set_rotation(rotation)
        lbl.set_horizontalalignment(ha)
        lbl.set_verticalalignment(va)
        lbl.set_rotation_mode("anchor")
        lbl.set_fontsize(fontsize)
        lbl.set_fontweight(weight)


def plot_fig7_physiospace_mission_profile():
    """Generates Figure 7 and exports to manuscript/figures and docs/figures."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_FIG_DIR.mkdir(parents=True, exist_ok=True)

    df_full, df_summary = compute_mission_physiospace_scores()
    dim_names = list(PHYSIOSPACE_DIMENSIONS.keys())
    clean_dim_names = [
        "Hypoxia & Anaerobiosis",
        "Osmotic & Dehydration Stress",
        "Mechanosensory & Cell Wall Strain",
        "Aquaporin Hydraulic Flux",
        "Oxidative Stress & ROS Buffering",
        "Energy Starvation (SnRK1)",
        "Abscisic Acid (ABA) Transduction",
        "Ethylene & Impedance Signaling",
        "Stomatal Resistance & Closure",
        "Thermal & Chaperone Protection",
    ]

    fig = plt.figure(figsize=(17.5, 12.0), dpi=300)
    gs = GridSpec(2, 2, height_ratios=[1.15, 0.95], width_ratios=[1.25, 0.95], hspace=0.36, wspace=0.28)

    # -------------------------------------------------------------
    # PANEL A: Master PhysioSpace Autodecoder Heatmap (Blue-White-Red)
    # -------------------------------------------------------------
    ax_a = fig.add_subplot(gs[0, 0])

    # Construct matrix: 10 dimensions x 12 columns (6 phases x 2 organs: Shoot, Root)
    col_labels = []
    matrix_data = []

    phases_order = ["M1", "M2", "M3", "M6", "M4", "M5"]
    phase_titles = {
        "M1": "M1: Earth\n101kPa 21%O₂",
        "M2": "M2: Staged\n70kPa 26%O₂",
        "M3": "M3: Expl. Hab\n56.5kPa 34%O₂ (50%RH)",
        "M6": "M6: BLiSS Rescue\n56.5kPa 34%O₂ (80%RH)",
        "M4": "M4: Uncomp. Air\n50kPa 21%O₂",
        "M5": "M5: Extreme\n5kPa 21%O₂",
    }

    cols_order = []
    for pid in phases_order:
        cols_order.append((pid, "Shoot", f"{phase_titles[pid]}\n[Shoot]"))
        cols_order.append((pid, "Root", f"{phase_titles[pid]}\n[Root]"))

    heatmap_df = pd.DataFrame(index=clean_dim_names, columns=[c[2] for c in cols_order], dtype=float)

    for orig_dim, clean_dim in zip(dim_names, clean_dim_names):
        for pid, organ, col_name in cols_order:
            val = df_full[(df_full["Phase_ID"] == pid) & (df_full["Organ"] == organ)][orig_dim].values[0]
            heatmap_df.loc[clean_dim, col_name] = val

    # Plot heatmap with Blue-White-Red
    vmin, vmax = -3.0, +3.0
    im_a = sns.heatmap(
        heatmap_df,
        cmap=BLUE_WHITE_RED_CMAP,
        vmin=vmin,
        vmax=vmax,
        center=0.0,
        cbar=True,
        cbar_kws={
            "label": "PhysioSpace Stress Score (z-score vs. Earth Baseline)\nLow / Suppressed (Blue)   |   Neutral / Homeostasis (White)   |   High / Activated (Red)",
            "orientation": "horizontal",
            "pad": 0.22,
            "shrink": 0.82,
            "aspect": 30,
        },
        linewidths=0.75,
        linecolor="#f0f0f0",
        annot=True,
        fmt=".2f",
        annot_kws={"fontsize": 7.5, "fontweight": "bold"},
        ax=ax_a,
    )

    ax_a.set_title("A   PhysioSpace Stress Autodecoder Across the NASA Exploration Atmosphere Mission Profile",
                   loc="left", fontsize=11, fontweight="bold", pad=20)
    _anchor_xticks(ax_a, rotation=35, ha="right", va="top", fontsize=8.0, weight="medium")
    ax_a.tick_params(axis="y", labelsize=8.5)

    # Highlight column groups (Nominal M3 vs BLiSS M6 Rescue) with clean dashed brackets
    ax_a.axvline(4, color="#008080", linestyle="--", linewidth=1.5, alpha=0.8) # Before M3
    ax_a.axvline(8, color="#008080", linestyle="--", linewidth=1.5, alpha=0.8) # After M6 rescue
    ax_a.text(6.0, -0.25, "[ Exploration Baseline (M3)  vs.  BLiSS Rescue (M6) ]",
              ha="center", va="bottom", fontsize=8.2, fontweight="bold", color="#008080")

    # -------------------------------------------------------------
    # PANEL B: PhysioSpace 2D Ordination Trajectory (Hypoxia vs. Osmotic)
    # -------------------------------------------------------------
    ax_b = fig.add_subplot(gs[0, 1])

    # Plot coordinates for Shoot and Root
    # x = Hypoxia Score, y = Osmotic/Dehydration Score
    phase_colors = {
        "M1": "#2b5c8f", # Navy
        "M2": "#008080", # Teal
        "M3": "#d95f02", # Orange
        "M6": "#2ca02c", # Emerald Green (Rescue)
        "M4": "#7570b3", # Purple
        "M5": "#e7298a", # Magenta
    }

    # Draw quadrant shading
    ax_b.axhline(0, color="#cccccc", linestyle="-", linewidth=1.0, zorder=1)
    ax_b.axvline(0, color="#cccccc", linestyle="-", linewidth=1.0, zorder=1)
    ax_b.axhspan(1.0, 3.8, xmin=0.0, xmax=0.35, color="#fee8c8", alpha=0.35, zorder=0) # Pure Osmotic Zone
    ax_b.axvspan(1.0, 4.0, ymin=0.0, ymax=0.35, color="#e0f3f8", alpha=0.35, zorder=0) # Pure Hypoxic Zone
    ax_b.axhspan(1.0, 3.8, xmin=0.35, xmax=1.0, color="#fbb4ae", alpha=0.25, zorder=0) # Compound Emergency

    ax_b.text(-0.85, 3.5, "Boundary-Layer Transpiration\n& Osmotic Stress Zone",
              fontsize=8.0, fontweight="bold", color="#b2182b", ha="left")
    ax_b.text(2.2, -0.65, "Core Hypoxic\nAnaerobiosis Zone",
              fontsize=8.0, fontweight="bold", color="#2166ac", ha="left")
    ax_b.text(2.1, 3.55, "Compound Catastrophic\nEmergency Zone",
              fontsize=8.0, fontweight="bold", color="#67001f", ha="left")

    # Plot points and trajectory arrows
    shoot_pts = {}
    for pid in phases_order:
        sub = df_full[(df_full["Phase_ID"] == pid) & (df_full["Organ"] == "Shoot")]
        x = sub["Hypoxia_Anaerobiosis"].values[0]
        y = sub["Osmotic_Drought_Dehydration"].values[0]
        shoot_pts[pid] = (x, y)
        ax_b.scatter(x, y, s=140, color=phase_colors[pid], edgecolors="black", linewidth=1.2, zorder=5)

    # Label points with clean non-overlapping offsets
    offsets = {
        "M1": (0.1, -0.32),
        "M2": (0.12, -0.22),
        "M3": (-0.18, 0.28),
        "M6": (0.15, 0.15),
        "M4": (0.18, -0.30),
        "M5": (-0.85, -0.38),
    }
    for pid, (x, y) in shoot_pts.items():
        dx, dy = offsets[pid]
        pname = [p["name"] for p in MISSION_PHASES if p["phase_id"] == pid][0]
        ax_b.annotate(
            f"{pid}: {pname}",
            xy=(x, y),
            xytext=(x + dx, y + dy),
            fontsize=7.5,
            fontweight="bold",
            color=phase_colors[pid],
            arrowprops=dict(arrowstyle="->", color=phase_colors[pid], lw=1.0),
            zorder=6
        )

    # Trajectory Arrow 1: M1 -> M2 -> M3 (Moves strictly upward into Osmotic space, ZERO hypoxia!)
    ax_b.annotate("", xy=shoot_pts["M2"], xytext=shoot_pts["M1"],
                  arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.8, linestyle=":"))
    ax_b.annotate("", xy=shoot_pts["M3"], xytext=shoot_pts["M2"],
                  arrowprops=dict(arrowstyle="-|>", color="#d95f02", lw=2.2))

    # Trajectory Arrow 2: M3 -> M6 (BLiSS Rescue drops straight down back to Homeostasis!)
    ax_b.annotate("", xy=shoot_pts["M6"], xytext=shoot_pts["M3"],
                  arrowprops=dict(arrowstyle="-|>", color="#2ca02c", lw=2.8))
    ax_b.text(
        0.85, 0.95,
        "Engineered 80% RH Rescue\n(Direct Return to Homeostasis)",
        color="#2ca02c", fontsize=8.0, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="#e8f5e9", ec="#2ca02c", lw=1.2)
    )

    # Trajectory Arrow 3: M3 -> M4 -> M5 (Emergency decompression shoots diagonally into high hypoxia!)
    ax_b.annotate("", xy=shoot_pts["M4"], xytext=shoot_pts["M3"],
                  arrowprops=dict(arrowstyle="-|>", color="#7570b3", lw=1.5, linestyle="--"))
    ax_b.annotate("", xy=shoot_pts["M5"], xytext=shoot_pts["M4"],
                  arrowprops=dict(arrowstyle="-|>", color="#e7298a", lw=1.8, linestyle="--"))

    ax_b.set_xlabel("PhysioSpace Hypoxia / Anaerobic Dimension (z-score)", fontsize=9.0, fontweight="semibold")
    ax_b.set_ylabel("PhysioSpace Osmotic / Dehydration Dimension (z-score)", fontsize=9.0, fontweight="semibold")
    ax_b.set_xlim(-1.0, 3.8)
    ax_b.set_ylim(-0.8, 3.8)
    ax_b.set_title("B   2D PhysioSpace Ordination: Mission Phase Decompression Trajectory",
                   loc="left", fontsize=11, fontweight="bold", pad=12)
    ax_b.grid(True, linestyle=":", alpha=0.5)

    # -------------------------------------------------------------
    # PANEL C: Organ-Specific Stress Partitioning (Shoot vs. Root in M3 vs M6)
    # -------------------------------------------------------------
    ax_c = fig.add_subplot(gs[1, 0])

    key_dims = [
        "Osmotic_Drought_Dehydration",
        "Mechanosensory_CellWall",
        "Aquaporin_WaterFlux",
        "Stomatal_Resistance",
        "Hypoxia_Anaerobiosis",
        "Energy_Starvation_SnRK1",
    ]
    clean_key_labels = [
        "Osmotic / Desiccation",
        "Cell Wall Mechanostress",
        "Aquaporin Hydraulic Flux",
        "Stomatal Resistance",
        "Hypoxia / Anaerobic",
        "SnRK1 Energy Starvation",
    ]

    x_idx = np.arange(len(key_dims))
    bar_width = 0.20

    # Values for Shoot M3, Root M3, Shoot M6, Root M6
    s_m3 = [df_full[(df_full["Phase_ID"] == "M3") & (df_full["Organ"] == "Shoot")][d].values[0] for d in key_dims]
    r_m3 = [df_full[(df_full["Phase_ID"] == "M3") & (df_full["Organ"] == "Root")][d].values[0] for d in key_dims]
    s_m6 = [df_full[(df_full["Phase_ID"] == "M6") & (df_full["Organ"] == "Shoot")][d].values[0] for d in key_dims]
    r_m6 = [df_full[(df_full["Phase_ID"] == "M6") & (df_full["Organ"] == "Root")][d].values[0] for d in key_dims]

    rects1 = ax_c.bar(x_idx - 1.5 * bar_width, s_m3, bar_width, label="Shoot (M3: 56.5 kPa / 50% RH)",
                      color="#d95f02", edgecolor="black", linewidth=0.8)
    rects2 = ax_c.bar(x_idx - 0.5 * bar_width, r_m3, bar_width, label="Root (M3: 56.5 kPa / 50% RH)",
                      color="#fdbe85", edgecolor="black", linewidth=0.8)
    rects3 = ax_c.bar(x_idx + 0.5 * bar_width, s_m6, bar_width, label="Shoot (M6: BLiSS Rescue 80% RH)",
                      color="#2ca02c", edgecolor="black", linewidth=0.8)
    rects4 = ax_c.bar(x_idx + 1.5 * bar_width, r_m6, bar_width, label="Root (M6: BLiSS Rescue 80% RH)",
                      color="#a1d99b", edgecolor="black", linewidth=0.8)

    ax_c.axhline(0, color="black", linestyle="-", linewidth=0.9)
    ax_c.set_xticks(x_idx)
    ax_c.set_xticklabels(clean_key_labels)
    _anchor_xticks(ax_c, rotation=28, ha="right", va="top", fontsize=8.5, weight="medium")
    ax_c.set_ylabel("PhysioSpace Stress Score (z-score)", fontsize=9.0, fontweight="semibold")
    ax_c.set_ylim(-0.6, 2.4)
    ax_c.set_title("C   Organ-Specific Stress Partitioning: Shoot vs. Root Divergence & Rescue",
                   loc="left", fontsize=11, fontweight="bold", pad=12)
    ax_c.legend(frameon=True, fontsize=8.0, loc="upper right", framealpha=0.9)
    ax_c.grid(True, axis="y", linestyle=":", alpha=0.5)

    # -------------------------------------------------------------
    # PANEL D: Engineered Relative Humidity Rescue Delta (M3 vs. M6)
    # -------------------------------------------------------------
    ax_d = fig.add_subplot(gs[1, 1])

    # Delta = M6 (80% RH) - M3 (50% RH) in Shoot
    deltas = []
    for d in dim_names:
        m3_val = df_full[(df_full["Phase_ID"] == "M3") & (df_full["Organ"] == "Shoot")][d].values[0]
        m6_val = df_full[(df_full["Phase_ID"] == "M6") & (df_full["Organ"] == "Shoot")][d].values[0]
        deltas.append(m6_val - m3_val)

    sorted_indices = np.argsort(deltas)
    sorted_labels = [clean_dim_names[i] for i in sorted_indices]
    sorted_deltas = [deltas[i] for i in sorted_indices]

    # Bar colors: Blue for negative (stress reduction / rescue), Red for positive
    bar_colors = ["#2166ac" if d < 0 else "#b2182b" for d in sorted_deltas]

    y_pos = np.arange(len(sorted_labels))
    bars = ax_d.barh(y_pos, sorted_deltas, color=bar_colors, edgecolor="black", linewidth=0.8, height=0.68)
    ax_d.axvline(0, color="black", linestyle="-", linewidth=1.0)

    # Add numeric labels to bars
    for bar, delta in zip(bars, sorted_deltas):
        offset = -0.06 if delta < 0 else 0.06
        ha = "right" if delta < 0 else "left"
        ax_d.text(delta + offset, bar.get_y() + bar.get_height() / 2, f"{delta:+.2f}",
                  va="center", ha=ha, fontsize=7.5, fontweight="bold",
                  color="#2166ac" if delta < 0 else "#b2182b")

    ax_d.set_yticks(y_pos)
    ax_d.set_yticklabels(sorted_labels, fontsize=8.0)
    ax_d.set_xlabel("Stress Score Delta: Δz = z(80% RH) − z(50% RH)\n(Negative / Blue = Successful Stress Extinction)",
                    fontsize=8.5, fontweight="semibold")
    ax_d.set_xlim(-2.3, 0.5)
    ax_d.set_title("D   Engineered BLiSS Humidity Countermeasure (Δz Stress Reduction in Shoot)",
                   loc="left", fontsize=11, fontweight="bold", pad=12)
    ax_d.grid(True, axis="x", linestyle=":", alpha=0.5)

    # Annotate key insight in upper-left whitespace (y=1.5 to 3.5 is empty in the negative zone)
    ax_d.text(
        -2.18, 1.8,
        "Total Hypobaric Rescue:\n• Osmotic Stress: -1.90 z\n• Stomatal Restr.: -1.76 z\n• Cell Wall Strain: -1.70 z\n• Aquaporin Flux: -1.60 z",
        fontsize=7.5, fontweight="bold", color="#053061",
        bbox=dict(boxstyle="round,pad=0.4", fc="#e8f4f8", ec="#2166ac", lw=1.2)
    )

    # Final tight layout and save
    plt.tight_layout()

    out_manuscript = FIG_DIR / "fig7_physiospace_mission_profile_autodecoder.png"
    out_docs = DOCS_FIG_DIR / "fig7_physiospace_mission_profile_autodecoder.png"
    out_brain = BRAIN_DIR / "fig7_physiospace_mission_profile_autodecoder.png"

    plt.savefig(out_manuscript, dpi=300, bbox_inches="tight")
    plt.savefig(out_docs, dpi=300, bbox_inches="tight")
    plt.savefig(out_brain, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Figure 7 successfully generated:")
    print(f"  Manuscript figure: {out_manuscript}")
    print(f"  Docs figure:       {out_docs}")
    print(f"  Brain artifact:    {out_brain}")


if __name__ == "__main__":
    plot_fig7_physiospace_mission_profile()
