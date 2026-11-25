from manim import *
import numpy as np

# Color Palette (3Blue1Brown-inspired on Deep Slate)
BG_COLOR = "#0F172A"
CYAN = "#38BDF8"
EMERALD = "#10B981"
AMBER = "#F59E0B"
GOLD = "#FBBF24"
RED_ACCENT = "#EF4444"
SLATE_LIGHT = "#94A3B8"
SLATE_CARD = "#1E293B"
WHITE_GLOW = "#F8FAFC"


class GaussianEliminationFull(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.act1_intro()
        self.act2_setup()
        self.act3_forward_elimination()
        self.act4_back_substitution()
        self.act5_special_cases()
        self.act6_summary()

    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------
    def make_panel_card(self, width=5.8, height=6.4, color=SLATE_CARD, stroke=SLATE_LIGHT):
        return RoundedRectangle(
            corner_radius=0.18,
            width=width,
            height=height,
            fill_color=color,
            fill_opacity=0.75,
            stroke_color=stroke,
            stroke_width=1.5,
        )

    def make_bracket(self, height=2.3, width=0.18, is_left=True, color=WHITE_GLOW):
        sign = 1 if is_left else -1
        b = VMobject(color=color, stroke_width=3)
        b.set_points_as_corners([
            [sign * width, height / 2, 0],
            [0, height / 2, 0],
            [0, -height / 2, 0],
            [sign * width, -height / 2, 0],
        ])
        return b

    def make_augmented_matrix(self, rows, v_line_color=SLATE_LIGHT):
        """
        Builds a clean augmented matrix [A | b] using Text + vector brackets.
        """
        entries = []
        for r in rows:
            row_mobs = [Text(str(val), font_size=28, color=WHITE_GLOW) for val in r]
            entries.append(row_mobs)

        grid = VGroup()
        col_x = [-1.45, -0.65, 0.15, 1.15]
        row_y = [0.7, 0.0, -0.7]

        for i in range(3):
            for j in range(4):
                mob = entries[i][j]
                mob.move_to([col_x[j], row_y[i], 0])
                grid.add(mob)

        divider = DashedLine(
            start=[0.65, 1.05, 0],
            end=[0.65, -1.05, 0],
            color=v_line_color,
            stroke_width=2,
            dash_length=0.08,
        )

        left_bracket = self.make_bracket(height=2.2, width=0.16, is_left=True).move_to([-1.92, 0, 0])
        right_bracket = self.make_bracket(height=2.2, width=0.16, is_left=False).move_to([1.62, 0, 0])

        mat_group = VGroup(left_bracket, grid, divider, right_bracket)
        return mat_group, entries

    def make_plane(self, axes, normal, d, u_range=(-1.5, 4.5), v_range=(-1.5, 4.5), color=CYAN, opacity=0.38):
        """
        Creates a 3D plane n_x x + n_y y + n_z z = d in axes coordinates.
        """
        nx, ny, nz = normal
        if abs(nz) >= abs(nx) and abs(nz) >= abs(ny) and abs(nz) > 1e-6:
            def param(u, v):
                z = (d - nx * u - ny * v) / nz
                return axes.c2p(u, v, z)
        elif abs(ny) >= abs(nx) and abs(ny) > 1e-6:
            def param(u, v):
                y = (d - nx * u - nz * v) / ny
                return axes.c2p(u, y, v)
        else:
            def param(u, v):
                x = (d - ny * u - nz * v) / nx
                return axes.c2p(x, u, v)

        return Surface(
            param,
            u_range=u_range,
            v_range=v_range,
            resolution=(12, 12),
            fill_color=color,
            fill_opacity=opacity,
            stroke_color=color,
            stroke_width=0.6,
            stroke_opacity=0.5,
        )

    # -------------------------------------------------------------------------
    # ACT 1: REAL-WORLD MOTIVATION & THE CORE IDEA (0:00 - 0:40 | ~40s)
    # -------------------------------------------------------------------------
    def act1_intro(self):
        # 0:00 - 0:15: Title Card
        title = Text(
            "Gaussian Elimination",
            font_size=56,
            weight=BOLD,
            color=WHITE_GLOW,
        ).shift(UP * 0.6)

        subtitle_main = Text(
            "From Chaos to Clarity",
            font_size=34,
            color=CYAN,
        ).next_to(title, DOWN, buff=0.25)

        subtitle_course = Text(
            "B.Tech Engineering Mathematics — Linear Systems",
            font_size=22,
            color=SLATE_LIGHT,
        ).next_to(subtitle_main, DOWN, buff=0.4)

        underline = Line(LEFT * 3.5, RIGHT * 3.5, color=GOLD, stroke_width=2.5).next_to(
            subtitle_main, DOWN, buff=0.18
        )

        self.play(Write(title, run_time=2.5, rate_func=smooth))
        self.play(
            FadeIn(subtitle_main, shift=UP * 0.2, run_time=2.0),
            Create(underline, run_time=2.0),
        )
        self.play(FadeIn(subtitle_course, run_time=2.0))
        self.wait(6.5)

        self.play(
            FadeOut(title, shift=UP * 0.3, run_time=1.5),
            FadeOut(subtitle_main, shift=UP * 0.3, run_time=1.5),
            FadeOut(underline, run_time=1.2),
            FadeOut(subtitle_course, run_time=1.2),
        )

        # 0:15 - 0:40: Engineering motivation -> 3x3 system
        eng_header = Text(
            "Why Linear Systems Matter in Engineering",
            font_size=32,
            weight=BOLD,
            color=CYAN,
        ).to_edge(UP, buff=0.5)

        circuit_box = RoundedRectangle(
            corner_radius=0.15, width=4.6, height=3.0,
            color=SLATE_LIGHT, fill_color=SLATE_CARD, fill_opacity=0.6
        ).shift(LEFT * 3.2 + DOWN * 0.2)

        loop1 = Circle(radius=0.55, color=CYAN, stroke_width=3).move_to(circuit_box.get_center() + LEFT * 0.8)
        loop2 = Circle(radius=0.55, color=EMERALD, stroke_width=3).move_to(circuit_box.get_center() + RIGHT * 0.8)
        i1_lbl = Text("I₁", color=CYAN, font_size=26).move_to(loop1)
        i2_lbl = Text("I₂", color=EMERALD, font_size=26).move_to(loop2)
        circuit_caption = Text("Mesh Currents & Structural Trusses", font_size=20, color=SLATE_LIGHT).next_to(
            circuit_box, DOWN, buff=0.2
        )
        eng_group = VGroup(circuit_box, loop1, loop2, i1_lbl, i2_lbl, circuit_caption)

        eqs = Text(
            "  x +  y +  z =  6\n"
            "2x + 3y +  z = 11\n"
            "  x −  y + 2z =  5",
            font_size=32,
            color=WHITE_GLOW,
            line_spacing=1.4,
        ).shift(RIGHT * 2.5 + DOWN * 0.2)

        arrow = Arrow(
            circuit_box.get_right(), eqs.get_left(),
            buff=0.3, color=GOLD, stroke_width=3
        )

        self.play(FadeIn(eng_header, run_time=1.5))
        self.play(FadeIn(eng_group, run_time=2.5))
        self.play(GrowArrow(arrow, run_time=1.5), Write(eqs, run_time=3.0))
        self.wait(5.0)

        thesis = Text(
            "Solving coupled equations directly is messy.\nGaussian Elimination systematically decouples them without changing the answer.",
            font_size=23,
            color=GOLD,
            line_spacing=1.3,
        ).to_edge(DOWN, buff=0.55)

        self.play(FadeIn(thesis, shift=UP * 0.2, run_time=2.2))
        self.wait(7.0)

        self.play(
            FadeOut(eng_header, run_time=1.0),
            FadeOut(eng_group, run_time=1.0),
            FadeOut(arrow, run_time=1.0),
            FadeOut(thesis, run_time=1.0),
            FadeOut(eqs, run_time=1.0),
        )

    # -------------------------------------------------------------------------
    # ACT 2: AUGMENTED MATRIX & 3D GEOMETRIC SETUP (0:40 - 1:25 | ~45s)
    # -------------------------------------------------------------------------
    def act2_setup(self):
        left_card = self.make_panel_card(width=5.6, height=6.5).to_edge(LEFT, buff=0.4)
        panel_title = Text("Algebraic View", font_size=24, weight=BOLD, color=CYAN).move_to(
            left_card.get_top() + DOWN * 0.4
        )

        eqs = Text(
            "  x +  y +  z =  6\n"
            "2x + 3y +  z = 11\n"
            "  x −  y + 2z =  5",
            font_size=28,
            color=WHITE_GLOW,
            line_spacing=1.35,
        ).move_to(left_card.get_center() + UP * 1.3)

        aug_label = Text("Augmented Matrix [A | b]", font_size=22, color=GOLD).move_to(
            left_card.get_center() + DOWN * 0.15
        )

        mat_group, mat_entries = self.make_augmented_matrix(
            [
                ["1", "1", "1", "6"],
                ["2", "3", "1", "11"],
                ["1", "-1", "2", "5"],
            ]
        )
        mat_group.move_to(left_card.get_center() + DOWN * 1.45)

        self.add_fixed_in_frame_mobjects(left_card, panel_title, eqs, aug_label, mat_group)
        left_card.set_opacity(0)
        panel_title.set_opacity(0)
        eqs.set_opacity(0)
        aug_label.set_opacity(0)
        mat_group.set_opacity(0)

        self.play(
            left_card.animate.set_opacity(0.75),
            panel_title.animate.set_opacity(1),
            eqs.animate.set_opacity(1),
            run_time=2.5,
        )
        self.wait(3.5)
        self.play(
            aug_label.animate.set_opacity(1),
            mat_group.animate.set_opacity(1),
            run_time=3.0,
        )
        self.wait(4.5)

        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        axes = ThreeDAxes(
            x_range=[-1, 5, 1],
            y_range=[-1, 5, 1],
            z_range=[-1, 5, 1],
            x_length=5.5,
            y_length=5.5,
            z_length=4.8,
            axis_config={"color": SLATE_LIGHT, "stroke_width": 1.8},
        ).shift(RIGHT * 2.5 + DOWN * 0.2)

        x_lbl = Text("x", font_size=22, color=SLATE_LIGHT).move_to(axes.c2p(5.3, 0, 0))
        y_lbl = Text("y", font_size=22, color=SLATE_LIGHT).move_to(axes.c2p(0, 5.3, 0))
        z_lbl = Text("z", font_size=22, color=SLATE_LIGHT).move_to(axes.c2p(0, 0, 5.3))

        self.play(Create(axes, run_time=2.0), FadeIn(x_lbl, y_lbl, z_lbl))

        p1 = self.make_plane(axes, (1, 1, 1), 6, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=CYAN, opacity=0.35)
        p2 = self.make_plane(axes, (2, 3, 1), 11, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=EMERALD, opacity=0.35)
        p3 = self.make_plane(axes, (1, -1, 2), 5, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=AMBER, opacity=0.35)

        self.play(FadeIn(p1, run_time=2.2))
        self.play(FadeIn(p2, run_time=2.2))
        self.play(FadeIn(p3, run_time=2.2))
        self.wait(4.0)

        inter_line = Line3D(
            start=axes.c2p(7 - 2 * 1.5, -1 + 1.5, 1.5),
            end=axes.c2p(7 - 2 * 4.0, -1 + 4.0, 4.0),
            color=WHITE_GLOW,
            thickness=0.03,
        )
        self.play(Create(inter_line, run_time=1.8))

        sol_dot = Dot3D(point=axes.c2p(1, 2, 3), radius=0.14, color=WHITE_GLOW)
        sol_halo = Dot3D(point=axes.c2p(1, 2, 3), radius=0.26, color=GOLD).set_opacity(0.45)

        sol_badge = Text("Solution: (1, 2, 3)", font_size=24, color=GOLD).to_corner(UR, buff=0.45)
        self.add_fixed_in_frame_mobjects(sol_badge)
        sol_badge.set_opacity(0)

        self.play(
            FadeIn(sol_dot, scale=0.5, run_time=1.5),
            FadeIn(sol_halo, scale=0.5, run_time=1.5),
            sol_badge.animate.set_opacity(1),
        )

        callout = Text(
            "Every valid row operation rotates or tilts these planes,\nbut keeps this intersection point locked in place.",
            font_size=19,
            color=WHITE_GLOW,
        ).to_edge(DOWN, buff=0.35).shift(RIGHT * 2.5)
        self.add_fixed_in_frame_mobjects(callout)
        callout.set_opacity(0)
        self.play(callout.animate.set_opacity(1), run_time=2.2)
        self.wait(8.0)

        self.left_card = left_card
        self.panel_title = panel_title
        self.eqs_act2 = eqs
        self.aug_label = aug_label
        self.mat_group = mat_group
        self.mat_entries = mat_entries
        self.axes = axes
        self.axis_labels = VGroup(x_lbl, y_lbl, z_lbl)
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.inter_line = inter_line
        self.sol_dot = sol_dot
        self.sol_halo = sol_halo
        self.sol_badge = sol_badge

        self.play(FadeOut(callout, run_time=1.0), FadeOut(inter_line, run_time=1.0))
        self.remove_fixed_in_frame_mobjects(callout)

    # -------------------------------------------------------------------------
    # ACT 3: FORWARD ELIMINATION TO ROW ECHELON FORM (1:25 - 2:45 | ~80s)
    # -------------------------------------------------------------------------
    def act3_forward_elimination(self):
        ref_card = RoundedRectangle(
            corner_radius=0.15, width=7.2, height=3.4,
            fill_color=SLATE_CARD, fill_opacity=0.95,
            stroke_color=GOLD, stroke_width=2,
        )
        ref_title = Text("3 Elementary Row Operations", font_size=28, weight=BOLD, color=GOLD).move_to(
            ref_card.get_top() + DOWN * 0.45
        )
        ops = Text(
            "1. Swap:  Rᵢ ↔ Rⱼ\n"
            "2. Scale:  Rᵢ ← k Rᵢ   (k ≠ 0)\n"
            "3. Add/Subtract:  Rᵢ ← Rᵢ + k Rⱼ",
            font_size=24,
            color=WHITE_GLOW,
            line_spacing=1.4,
        ).move_to(ref_card.get_center() + DOWN * 0.25)

        ref_group = VGroup(ref_card, ref_title, ops).move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(ref_group)
        self.play(FadeIn(ref_group, scale=0.95, run_time=2.2))
        self.wait(8.0)

        compact_ops = Text(
            "Rᵢ ↔ Rⱼ  |  k Rᵢ  |  Rᵢ + k Rⱼ",
            font_size=18,
            color=SLATE_LIGHT,
        ).to_corner(DL, buff=0.55).shift(RIGHT * 0.15)
        self.add_fixed_in_frame_mobjects(compact_ops)
        compact_ops.set_opacity(0)

        self.play(
            FadeOut(ref_group, run_time=1.5),
            compact_ops.animate.set_opacity(1),
        )
        self.remove_fixed_in_frame_mobjects(ref_group)

        self.play(FadeOut(self.eqs_act2, run_time=1.0))
        self.remove_fixed_in_frame_mobjects(self.eqs_act2)

        self.play(
            self.aug_label.animate.move_to(self.left_card.get_center() + UP * 1.9),
            self.mat_group.animate.move_to(self.left_card.get_center() + UP * 0.55),
            run_time=1.5,
        )

        # Eliminating Column 1
        pivot1_box = SurroundingRectangle(self.mat_entries[0][0], color=GOLD, buff=0.1, stroke_width=2.5)
        self.add_fixed_in_frame_mobjects(pivot1_box)
        self.play(Create(pivot1_box, run_time=1.2))

        op1_text = Text("R₂ ← R₂ − 2R₁", font_size=24, color=EMERALD).move_to(
            self.left_card.get_center() + DOWN * 1.05
        )
        op2_text = Text("R₃ ← R₃ − R₁", font_size=24, color=AMBER).move_to(
            self.left_card.get_center() + DOWN * 1.65
        )

        self.add_fixed_in_frame_mobjects(op1_text, op2_text)
        op1_text.set_opacity(0)
        op2_text.set_opacity(0)

        self.play(op1_text.animate.set_opacity(1), run_time=1.5)
        self.wait(1.5)

        mat2_group, mat2_entries = self.make_augmented_matrix(
            [
                ["1", "1", "1", "6"],
                ["0", "1", "-1", "-1"],
                ["1", "-1", "2", "5"],
            ]
        )
        mat2_group.move_to(self.mat_group.get_center())
        self.add_fixed_in_frame_mobjects(mat2_group)
        mat2_group.set_opacity(0)

        p2_new = self.make_plane(self.axes, (0, 1, -1), -1, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=EMERALD, opacity=0.35)

        self.play(
            FadeOut(self.mat_group, run_time=1.0),
            mat2_group.animate.set_opacity(1),
            ReplacementTransform(self.p2, p2_new, run_time=3.5, rate_func=smooth),
        )
        self.remove_fixed_in_frame_mobjects(self.mat_group)
        self.p2 = p2_new
        self.mat_group = mat2_group
        self.mat_entries = mat2_entries
        self.wait(5.5)

        self.play(op2_text.animate.set_opacity(1), run_time=1.8)
        self.wait(2.5)

        mat3_group, mat3_entries = self.make_augmented_matrix(
            [
                ["1", "1", "1", "6"],
                ["0", "1", "-1", "-1"],
                ["0", "-2", "1", "-1"],
            ]
        )
        mat3_group.move_to(self.mat_group.get_center())
        self.add_fixed_in_frame_mobjects(mat3_group)
        mat3_group.set_opacity(0)

        p3_col1 = self.make_plane(self.axes, (0, -2, 1), -1, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=AMBER, opacity=0.35)

        self.play(
            FadeOut(self.mat_group, run_time=1.0),
            mat3_group.animate.set_opacity(1),
            ReplacementTransform(self.p3, p3_col1, run_time=3.5, rate_func=smooth),
        )
        self.remove_fixed_in_frame_mobjects(self.mat_group)
        self.p3 = p3_col1
        self.mat_group = mat3_group
        self.mat_entries = mat3_entries
        self.wait(5.5)

        # Eliminating Column 2 -> REF
        pivot2_box = SurroundingRectangle(self.mat_entries[1][1], color=GOLD, buff=0.1, stroke_width=2.5)
        self.add_fixed_in_frame_mobjects(pivot2_box)

        op3_text = Text("R₃ ← R₃ + 2R₂", font_size=24, color=AMBER).move_to(
            self.left_card.get_center() + DOWN * 1.35
        )
        self.add_fixed_in_frame_mobjects(op3_text)
        op3_text.set_opacity(0)

        self.play(
            FadeOut(pivot1_box, run_time=0.8),
            FadeOut(op1_text, run_time=0.8),
            FadeOut(op2_text, run_time=0.8),
            Create(pivot2_box, run_time=1.2),
            op3_text.animate.set_opacity(1),
        )
        self.remove_fixed_in_frame_mobjects(pivot1_box, op1_text, op2_text)
        self.wait(1.5)

        mat4_group, mat4_entries = self.make_augmented_matrix(
            [
                ["1", "1", "1", "6"],
                ["0", "1", "-1", "-1"],
                ["0", "0", "-1", "-3"],
            ]
        )
        mat4_group.move_to(self.mat_group.get_center())
        self.add_fixed_in_frame_mobjects(mat4_group)
        mat4_group.set_opacity(0)

        p3_flat = self.make_plane(self.axes, (0, 0, -1), -3, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=AMBER, opacity=0.38)

        self.play(
            FadeOut(self.mat_group, run_time=1.0),
            mat4_group.animate.set_opacity(1),
            ReplacementTransform(self.p3, p3_flat, run_time=3.5, rate_func=smooth),
        )
        self.remove_fixed_in_frame_mobjects(self.mat_group)
        self.p3 = p3_flat
        self.mat_group = mat4_group
        self.mat_entries = mat4_entries

        e00 = self.mat_entries[0][0].get_corner(DL) + DOWN * 0.08 + LEFT * 0.1
        e11 = self.mat_entries[1][1].get_corner(DL) + DOWN * 0.08 + LEFT * 0.1
        e22 = self.mat_entries[2][2].get_corner(DL) + DOWN * 0.08 + LEFT * 0.1
        e22_r = self.mat_entries[2][2].get_corner(DR) + DOWN * 0.08 + RIGHT * 0.1

        staircase = VMobject(color=GOLD, stroke_width=3.5)
        staircase.set_points_as_corners([
            e00,
            [e11[0], e00[1], 0],
            e11,
            [e22[0], e11[1], 0],
            e22,
            e22_r,
        ])
        ref_badge = Text("Row Echelon Form (REF)", font_size=22, weight=BOLD, color=GOLD).move_to(
            self.left_card.get_center() + DOWN * 2.0
        )
        self.add_fixed_in_frame_mobjects(staircase, ref_badge)
        ref_badge.set_opacity(0)

        self.play(
            FadeOut(pivot2_box, run_time=0.8),
            FadeOut(op3_text, run_time=0.8),
            Create(staircase, run_time=2.0),
            ref_badge.animate.set_opacity(1),
        )
        self.remove_fixed_in_frame_mobjects(pivot2_box, op3_text)
        self.staircase = staircase
        self.ref_badge = ref_badge
        self.compact_ops = compact_ops
        self.wait(8.0)

    # -------------------------------------------------------------------------
    # ACT 4: BACK-SUBSTITUTION & RREF (2:45 - 3:35 | ~50s)
    # -------------------------------------------------------------------------
    def act4_back_substitution(self):
        self.play(FadeOut(self.staircase, run_time=0.8), FadeOut(self.ref_badge, run_time=0.8))
        self.remove_fixed_in_frame_mobjects(self.staircase, self.ref_badge)

        mat5_group, mat5_entries = self.make_augmented_matrix(
            [
                ["1", "1", "1", "6"],
                ["0", "1", "-1", "-1"],
                ["0", "0", "1", "3"],
            ]
        )
        mat5_group.move_to(self.mat_group.get_center())
        self.add_fixed_in_frame_mobjects(mat5_group)
        mat5_group.set_opacity(0)

        self.play(
            FadeOut(self.mat_group, run_time=0.8),
            mat5_group.animate.set_opacity(1),
        )
        self.remove_fixed_in_frame_mobjects(self.mat_group)
        self.mat_group = mat5_group
        self.mat_entries = mat5_entries

        back_title = Text("Back-Substitution", font_size=22, weight=BOLD, color=CYAN).move_to(
            self.left_card.get_center() + DOWN * 0.95
        )
        step_z = Text("z = 3", font_size=24, color=AMBER).move_to(self.left_card.get_center() + DOWN * 1.4)
        step_y = Text("y − (3) = −1  ⇒  y = 2", font_size=22, color=EMERALD).move_to(
            self.left_card.get_center() + DOWN * 1.9
        )
        step_x = Text("x + (2) + (3) = 6  ⇒  x = 1", font_size=22, color=CYAN).move_to(
            self.left_card.get_center() + DOWN * 2.4
        )

        self.add_fixed_in_frame_mobjects(back_title, step_z, step_y, step_x)
        for m in [back_title, step_z, step_y, step_x]:
            m.set_opacity(0)

        self.play(back_title.animate.set_opacity(1), run_time=1.5)
        self.play(step_z.animate.set_opacity(1), run_time=2.2)
        self.wait(3.5)
        self.play(step_y.animate.set_opacity(1), run_time=2.5)
        self.wait(3.5)
        self.play(step_x.animate.set_opacity(1), run_time=2.5)
        self.wait(6.0)

        rref_group, _ = self.make_augmented_matrix(
            [
                ["1", "0", "0", "1"],
                ["0", "1", "0", "2"],
                ["0", "0", "1", "3"],
            ]
        )
        rref_group.move_to(self.mat_group.get_center())
        self.add_fixed_in_frame_mobjects(rref_group)
        rref_group.set_opacity(0)

        rref_badge = Text("Reduced Row Echelon Form (RREF)", font_size=20, weight=BOLD, color=GOLD).move_to(
            self.aug_label.get_center()
        )
        self.add_fixed_in_frame_mobjects(rref_badge)
        rref_badge.set_opacity(0)

        p1_ortho = self.make_plane(self.axes, (1, 0, 0), 1, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=CYAN, opacity=0.35)
        p2_ortho = self.make_plane(self.axes, (0, 1, 0), 2, u_range=(-0.5, 4.0), v_range=(-0.5, 4.0), color=EMERALD, opacity=0.35)

        self.play(
            FadeOut(self.mat_group, run_time=1.0),
            FadeOut(self.aug_label, run_time=1.0),
            rref_group.animate.set_opacity(1),
            rref_badge.animate.set_opacity(1),
            ReplacementTransform(self.p1, p1_ortho, run_time=3.5, rate_func=smooth),
            ReplacementTransform(self.p2, p2_ortho, run_time=3.5, rate_func=smooth),
        )
        self.remove_fixed_in_frame_mobjects(self.mat_group, self.aug_label)
        self.p1 = p1_ortho
        self.p2 = p2_ortho
        self.wait(8.0)

        fixed_to_clear = [
            self.left_card, self.panel_title, rref_badge, rref_group,
            back_title, step_z, step_y, step_x, self.compact_ops, self.sol_badge
        ]
        self.play(
            *[FadeOut(m, run_time=1.2) for m in fixed_to_clear],
            FadeOut(self.axes, run_time=1.2),
            FadeOut(self.axis_labels, run_time=1.2),
            FadeOut(self.p1, run_time=1.2),
            FadeOut(self.p2, run_time=1.2),
            FadeOut(self.p3, run_time=1.2),
            FadeOut(self.sol_dot, run_time=1.2),
            FadeOut(self.sol_halo, run_time=1.2),
        )
        self.remove_fixed_in_frame_mobjects(*fixed_to_clear)

    # -------------------------------------------------------------------------
    # ACT 5: B.TECH EXAM EDGE CASES — RANK & CONSISTENCY (3:35 - 4:15 | ~40s)
    # -------------------------------------------------------------------------
    def act5_special_cases(self):
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)

        header = Text(
            "B.Tech Exam Edge Cases: Rank & Consistency",
            font_size=32,
            weight=BOLD,
            color=GOLD,
        ).to_edge(UP, buff=0.45)

        card_a = self.make_panel_card(width=5.8, height=5.4, stroke=EMERALD).shift(LEFT * 3.2 + DOWN * 0.35)
        title_a = Text("Case A: Infinite Solutions", font_size=24, weight=BOLD, color=EMERALD).move_to(
            card_a.get_top() + DOWN * 0.4
        )
        rank_a = Text("Rank(A) = Rank([A|b]) < 3", font_size=22, color=WHITE_GLOW).move_to(
            card_a.get_top() + DOWN * 0.9
        )
        mat_a, entries_a = self.make_augmented_matrix(
            [
                ["1", "1", "1", "6"],
                ["0", "1", "-1", "-1"],
                ["0", "0", "0", "0"],
            ]
        )
        mat_a.scale(0.85).move_to(card_a.get_center() + UP * 0.25)
        row3_a = VGroup(*entries_a[2])
        box_a = SurroundingRectangle(row3_a, color=EMERALD, buff=0.08)
        desc_a = Text(
            "Free variable (z = t)\n3 planes intersect along a glowing LINE",
            font_size=19,
            color=SLATE_LIGHT,
            line_spacing=1.25,
        ).move_to(card_a.get_bottom() + UP * 0.65)

        card_b = self.make_panel_card(width=5.8, height=5.4, stroke=RED_ACCENT).shift(RIGHT * 3.2 + DOWN * 0.35)
        title_b = Text("Case B: No Solution (Inconsistent)", font_size=24, weight=BOLD, color=RED_ACCENT).move_to(
            card_b.get_top() + DOWN * 0.4
        )
        rank_b = Text("Rank(A) < Rank([A|b])", font_size=22, color=WHITE_GLOW).move_to(
            card_b.get_top() + DOWN * 0.9
        )
        mat_b, entries_b = self.make_augmented_matrix(
            [
                ["1", "1", "1", "6"],
                ["0", "1", "-1", "-1"],
                ["0", "0", "0", "5"],
            ]
        )
        mat_b.scale(0.85).move_to(card_b.get_center() + UP * 0.25)
        row3_b = VGroup(*entries_b[2])
        box_b = SurroundingRectangle(row3_b, color=RED_ACCENT, buff=0.08)
        desc_b = Text(
            "0 = 5 (Contradiction!)\nParallel planes never meet",
            font_size=19,
            color=RED_ACCENT,
            line_spacing=1.25,
        ).move_to(card_b.get_bottom() + UP * 0.65)

        self.play(FadeIn(header, run_time=1.2))
        self.play(
            FadeIn(card_a, run_time=1.8),
            FadeIn(title_a, run_time=1.8),
            Write(rank_a, run_time=1.8),
            FadeIn(mat_a, run_time=1.8),
            Create(box_a, run_time=1.5),
            FadeIn(desc_a, run_time=1.8),
        )
        self.wait(7.0)

        self.play(
            FadeIn(card_b, run_time=1.8),
            FadeIn(title_b, run_time=1.8),
            Write(rank_b, run_time=1.8),
            FadeIn(mat_b, run_time=1.8),
            Create(box_b, run_time=1.5),
            FadeIn(desc_b, run_time=1.8),
        )
        self.wait(8.5)

        self.play(
            FadeOut(header, run_time=1.2),
            FadeOut(card_a, title_a, rank_a, mat_a, box_a, desc_a, run_time=1.2),
            FadeOut(card_b, title_b, rank_b, mat_b, box_b, desc_b, run_time=1.2),
        )

    # -------------------------------------------------------------------------
    # ACT 6: SUMMARY & EXAM CHECKLIST (4:15 - 4:35 | ~20s)
    # -------------------------------------------------------------------------
    def act6_summary(self):
        summary_card = self.make_panel_card(width=9.5, height=4.8, stroke=GOLD)
        summary_title = Text(
            "Gaussian Elimination — Exam Checklist",
            font_size=34,
            weight=BOLD,
            color=GOLD,
        ).move_to(summary_card.get_top() + DOWN * 0.65)

        step1 = Text("1. Augment:  Write [A | b]", font_size=26, color=CYAN)
        step2 = Text("2. Forward Eliminate:  Use pivots to create zeros below the staircase (REF)", font_size=24, color=EMERALD)
        step3 = Text("3. Check Rank & Back-Substitute:  Verify consistency, then solve bottom-up", font_size=24, color=AMBER)

        steps_group = VGroup(step1, step2, step3).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(
            summary_card.get_center() + DOWN * 0.25
        )

        self.play(FadeIn(summary_card, run_time=1.5), Write(summary_title, run_time=2.0))
        self.play(FadeIn(step1, shift=RIGHT * 0.2, run_time=2.0))
        self.play(FadeIn(step2, shift=RIGHT * 0.2, run_time=2.0))
        self.play(FadeIn(step3, shift=RIGHT * 0.2, run_time=2.0))
        self.wait(7.0)

        self.play(
            FadeOut(summary_card, summary_title, steps_group, run_time=2.0)
        )
