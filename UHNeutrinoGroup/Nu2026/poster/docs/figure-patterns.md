# Figure inclusion patterns

Reference snippets extracted from the legacy `TMP_RESOURCES/poster_tmp.tex` (REVTeX two-column draft, since deleted). Use these when swapping body figure placeholders for real assets.

## 1. Overpic-style annotation overlay on a raster

For a raster figure (PNG/PDF) annotated with white-bordered call-out boxes and arrows pointing to features. Used in `poster_tmp.tex` for the RAT-PAC IBD visualization.

```latex
\usepackage[percent]{overpic}

\begin{overpic}[width=1.0\linewidth]{figures/RAT_PAC_IBD_run_6_5_crop.png}
  \put(16.5,90){\color{white}\vector(0,-1){5}}
  \put(0,93){\fcolorbox{white}{white!30}{%
    \parbox{70pt}{neutron capture
      ${\color{orange}n}\;{}^6\mathrm{Li} \to {}^3\mathrm{H}\;{}^4\mathrm{He}$}}}

  \put(67,45){\color{white}\vector(0,1){15}}
  \put(57,41){\fcolorbox{white}{white!30}{%
    \parbox{50pt}{positron\\ annihilation
      ${\color{red}e^+}\,e^- \to {\color{green}\gamma}\,{\color{green}\gamma}$}}}

  \put(81,86){\color{white}\vector(0,-1){15}}
  \put(65,85){\fcolorbox{white}{white!30}{%
    \parbox{70pt}{inverse $\beta$ decay
      $\bar\nu_e\,{}^1\mathrm{H} \to {\color{red}e^+}\,{\color{orange}n}$}}}
\end{overpic}
```

Coordinates `(x,y)` are percentages of the image (0–100). `\fcolorbox{white}{white!30}` is the white-edge translucent label; `\parbox{Npt}` constrains text width. Use one `\put` per annotation.

## 2. Side-by-side binning matrices with directional arrows

A three-up tabular of related figures with arrow glyphs and angle labels below each, used for the binning-distribution panel.

```latex
\begin{tabular}{ccc}
  \includegraphics[width=0.32\linewidth]{figures/bin_dist_rot0_001wt.pdf} &
  \includegraphics[width=0.32\linewidth]{figures/bin_dist_rot30_001wt.pdf} &
  \includegraphics[width=0.32\linewidth]{figures/bin_dist_rot45_001wt.pdf} \\
\end{tabular}

\begin{tabular}{>{\centering\arraybackslash}p{0.32\linewidth}
                >{\centering\arraybackslash}p{0.32\linewidth}
                >{\centering\arraybackslash}p{0.32\linewidth}}
  \makebox[0.32\linewidth][c]{%
    \begin{picture}(20,20)
      \put(-5,13){\color{black}\vector(1,0){20}}
    \end{picture}} &
  \makebox[0.32\linewidth][c]{%
    \begin{picture}(20,20)
      \put(-3,17){\color{black}\vector(2,-1){18}}
    \end{picture}} &
  \makebox[0.32\linewidth][c]{%
    \begin{picture}(20,20)
      \put(-1,19){\color{black}\vector(1,-1){14}}
    \end{picture}} \\
  $\vartheta_\nu = 0^\circ$ & $\vartheta_\nu = -30^\circ$ & $\vartheta_\nu = -45^\circ$
\end{tabular}
```

The `\vector(dx,dy){length}` arrow direction (e.g. `(1,0)`, `(2,-1)`, `(1,-1)`) encodes the antineutrino wind angle visually below each matrix.

## 3. Geometry diagram via `picture` primitives

The detector + axes + neutrino-wind diagram (segmented cube, prompt/delayed segments, 3D axes, capture-angle arc), built with raw `\picture` primitives. Requires `\usepackage{pict2e}` for the `\arc` macro.

```latex
\setlength{\unitlength}{.1\linewidth}
\begin{picture}(10,5)
  % grid of segments
  \multiput(5,0)(.5,0){9}{\color{black}\line(0,1){4}}
  \multiput(5,0)(0,0.5){9}{\color{black}\line(1,0){4}}

  % perspective extension lines
  \multiput(5,4)(.5,0){9}{\color{black}\line(1,1){1}}
  \multiput(9,0)(0,.5){9}{\color{black}\line(1,1){1}}
  \put(10,1){\line(0,1){4}}
  \put(6,5){\line(1,0){4}}

  % prompt + delayed segment markers (thick vertical bars)
  \thicklines
  \multiput(6.5,2.50)(.025,0){20}{\color{black}\line(0,1){0.5}}
  \multiput(6,1.50)(.025,0){20}{\color{gray}\line(0,1){0.5}}
  \thinlines

  \put(0.8,4.7){prompt segment}
  \put(0.8,3.9){delayed segment}

  % 3D axes
  \put(1,1){\vector(-1,-1){1}}    % z
  \put(1,1){\vector(0,1){2}}      % y
  \put(1,1){\vector(1,0){2}}      % x
  \put(0,0.3){$z$} \put(0.7,2.8){$y$} \put(2.8,.7){$x$}

  % neutrino direction + angle arc
  \put(1,1){\vector(2,1){2}}
  \put(1,1){\arc[0,26]{1}}
  \put(2.7,2){$\nu$}

  % capture angle within prompt-segment-local frame
  \put(6.75,-0.1){\color{black!90}\vector(0,1){4.7}}
  \put(4.8,2.75){\color{black!90}\vector(1,0){4.8}}
  \put(6.8,4.55){$y'$} \put(9.2,2.4){$x'$}
  \put(5.85,2.1){$\theta_n^i$}
  \put(6.75,2.75){\color{blue}\arc[0,245]{0.65}}
  \put(6.75,2.75){\color{blue}\vector(-1,-2){0.5}}

  % neutrino wind arrows
  \multiput(3.5,0.5)(0,1){4}{\color{black}\vector(2,1){1}}
  \put(2,0){neutrino wind}
  \put(2.2,1.2){$\vartheta_\nu$}
\end{picture}
```

Key macros: `\multiput(start)(step){count}{thing}` for repeated grid lines; `\vector(dx,dy){length}` for arrows; `\arc[startDeg,endDeg]{radius}` for circular arcs.

When porting to TikZ for the Neutrino 2026 poster (round 2), the same shape primitives map to `\node[...]`, `\draw[->]`, and TikZ's `arc` operation.
