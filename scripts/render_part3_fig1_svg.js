/**
 * Professional 2-Tier Vector Diagram Renderer for Part 3 Fig 1:
 * Line of Action Five Singular Points and Meshing Path Geometry.
 * 
 * Standard Gear Pair: m=3.0 mm, z1=18, z2=54, alpha_0=20.0 deg, a=108.0 mm
 * Generates ISO 129-1 / DIN 3960 compliant technical SVG & 300 DPI PNG assets
 * from pure mathematical JSON geometry specifications and i18n dictionaries.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Base directories
const REPO_ROOT = path.resolve(__dirname, '../../');
const DATA_DIR = path.join(REPO_ROOT, 'blog/data');
const SPEC_FILE = path.join(DATA_DIR, 'specs/fig1_part3_spec.json');
const LOCALES_DIR = path.join(DATA_DIR, 'locales');
const PUBLIC_IMG_DIR = path.join(REPO_ROOT, 'blog/public/images/part3');

// Read geometry specification
const spec = JSON.parse(fs.readFileSync(SPEC_FILE, 'utf-8'));
const params = spec.parameters;

// Canvas & Viewport setup (Expanded for comfortable breathing room)
const CANVAS_W = 1260;
const CANVAS_H = 920;

// Geometry Coordinate Mapping:
// Pitch Point P(0, 0) maps to (cx, cy)
const cx = 610;
const cy = 325;
const scale = 13.8; // 1 mm = 13.8 px

function toSvgX(xMm) {
  return cx + xMm * scale;
}
function toSvgY(yMm) {
  return cy - yMm * scale; // SVG Y axis points downwards
}

// Color Palette (Engineering Standards)
const COLORS = {
  bg: '#ffffff',
  textMain: '#0f172a',
  textSub: '#334155',
  border: '#cbd5e1',
  cardBg: '#f8fafc',
  cardBorder: '#94a3b8',
  
  pinion: '#0284c7',       // Sky blue
  pinionLight: '#e0f2fe',
  gear: '#059669',         // Emerald green
  gearLight: '#ecfdf5',
  actionLine: '#dc2626',   // Crimson red
  pitchLine: '#7c3aed',    // Purple
  axisLine: '#94a3b8',     // Muted slate
  
  contactPoint: '#e11d48', // Rose red (A, E)
  contactLimit: '#7c3aed', // Purple (B, D)
  pitchPoint: '#ea580c',   // Orange (P)
  basePoint: '#2563eb',    // Blue (T1, T2)
  
  dimPb: '#4338ca',        // Indigo
  dimGa: '#ea580c',        // Orange / Gold
  dimBd: '#7c3aed',        // Violet
  
  bandActive: 'rgba(56, 189, 248, 0.40)', // Active contact AE
  bandSingle: 'rgba(245, 158, 11, 0.45)'  // Single contact BD
};

function escapeXml(unsafe) {
  if (typeof unsafe !== 'string') return unsafe;
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * Generates an SVG string for Part 3 Fig 1 for a given language.
 */
function generateSvgForLanguage(lang) {
  const dictFile = path.join(LOCALES_DIR, lang, 'fig1_part3_labels.json');
  const rawTr = JSON.parse(fs.readFileSync(dictFile, 'utf-8'));
  const tr = {};
  for (const [k, v] of Object.entries(rawTr)) {
    tr[k] = escapeXml(v);
  }

  // Pre-calculate landmark coordinates in SVG space
  const N1 = spec.landmarks.N1.coord;
  const N2 = spec.landmarks.N2.coord;
  const A = spec.landmarks.A.coord;
  const B = spec.landmarks.B.coord;
  const P = spec.landmarks.P.coord;
  const D = spec.landmarks.D.coord;
  const E = spec.landmarks.E.coord;

  const svgN1 = { x: toSvgX(N1[0]), y: toSvgY(N1[1]) };
  const svgN2 = { x: toSvgX(N2[0]), y: toSvgY(N2[1]) };
  const svgA = { x: toSvgX(A[0]), y: toSvgY(A[1]) };
  const svgB = { x: toSvgX(B[0]), y: toSvgY(B[1]) };
  const svgP = { x: toSvgX(P[0]), y: toSvgY(P[1]) };
  const svgD = { x: toSvgX(D[0]), y: toSvgY(D[1]) };
  const svgE = { x: toSvgX(E[0]), y: toSvgY(E[1]) };

  // Line of Action extended ends
  const alphaRad = params.alpha_deg * Math.PI / 180;
  const u_loa = [Math.cos(alphaRad), -Math.sin(alphaRad)];
  const norm_loa = [Math.sin(alphaRad), Math.cos(alphaRad)];

  const loaStartMm = [(spec.landmarks.N1.t - 3.2) * u_loa[0], (spec.landmarks.N1.t - 3.2) * u_loa[1]];
  const loaEndMm = [(spec.landmarks.N2.t + 3.2) * u_loa[0], (spec.landmarks.N2.t + 3.2) * u_loa[1]];
  const svgLoaStart = { x: toSvgX(loaStartMm[0]), y: toSvgY(loaStartMm[1]) };
  const svgLoaEnd = { x: toSvgX(loaEndMm[0]), y: toSvgY(loaEndMm[1]) };

  // Centers of circles
  const svgO1 = { x: toSvgX(0), y: toSvgY(params.r1) };
  const svgO2 = { x: toSvgX(0), y: toSvgY(-params.r2) };

  // Circular arc path generator
  function arcPath(centerSvg, radiusMm, startDeg, endDeg) {
    const rPx = radiusMm * scale;
    const rad1 = startDeg * Math.PI / 180;
    const rad2 = endDeg * Math.PI / 180;
    const x1 = centerSvg.x + rPx * Math.cos(rad1);
    const y1 = centerSvg.y - rPx * Math.sin(rad1);
    const x2 = centerSvg.x + rPx * Math.cos(rad2);
    const y2 = centerSvg.y - rPx * Math.sin(rad2);
    return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${rPx.toFixed(2)} ${rPx.toFixed(2)} 0 0 0 ${x2.toFixed(2)} ${y2.toFixed(2)}`;
  }

  // Dimension line generator:
  // Strictly parallel to the arrow line (exact vector angle in SVG space)
  function makeAlignedDim(p1Mm, p2Mm, offsetMm, text, color, isTopSide = true, anchorShift = 0, dimId = "") {
    const offX = norm_loa[0] * offsetMm;
    const offY = norm_loa[1] * offsetMm;

    // Dimension line endpoints in mm
    const d1Mm = [p1Mm[0] + offX, p1Mm[1] + offY];
    const d2Mm = [p2Mm[0] + offX, p2Mm[1] + offY];

    const svgP1 = { x: toSvgX(p1Mm[0]), y: toSvgY(p1Mm[1]) };
    const svgP2 = { x: toSvgX(p2Mm[0]), y: toSvgY(p2Mm[1]) };
    const svgD1 = { x: toSvgX(d1Mm[0]), y: toSvgY(d1Mm[1]) };
    const svgD2 = { x: toSvgX(d2Mm[0]), y: toSvgY(d2Mm[1]) };

    // Extension lines overshoot
    const extOvershoot = 2.0; // mm
    const ext1EndMm = [p1Mm[0] + norm_loa[0] * (offsetMm + (offsetMm > 0 ? extOvershoot : -extOvershoot)),
                       p1Mm[1] + norm_loa[1] * (offsetMm + (offsetMm > 0 ? extOvershoot : -extOvershoot))];
    const ext2EndMm = [p2Mm[0] + norm_loa[0] * (offsetMm + (offsetMm > 0 ? extOvershoot : -extOvershoot)),
                       p2Mm[1] + norm_loa[1] * (offsetMm + (offsetMm > 0 ? extOvershoot : -extOvershoot))];
    const svgExt1End = { x: toSvgX(ext1EndMm[0]), y: toSvgY(ext1EndMm[1]) };
    const svgExt2End = { x: toSvgX(ext2EndMm[0]), y: toSvgY(ext2EndMm[1]) };

    // Midpoint of dimension line
    const dx = svgD2.x - svgD1.x;
    const dy = svgD2.y - svgD1.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const unitX = dx / dist;
    const unitY = dy / dist;

    // Midpoint shifted along arrow line if anchorShift is given
    const midSvg = {
      x: (svgD1.x + svgD2.x) * 0.5 + unitX * anchorShift,
      y: (svgD1.y + svgD2.y) * 0.5 + unitY * anchorShift
    };

    // Vector angle of arrow line in SVG space:
    // dy/dx is positive downwards, angle is +alpha (~20.0 deg)
    const angleRad = Math.atan2(dy, dx);
    let angleDeg = angleRad * 180 / Math.PI;

    // Strict readability convention: keep text upright (-90 to +90 deg)
    if (angleDeg > 90) angleDeg -= 180;
    else if (angleDeg < -90) angleDeg += 180;

    // Offset text perpendicular to dimension line
    const textOffsetY = isTopSide ? -9 : 17;
    const textWidth = Math.max(text.length * 8.5 + 16, 80);

    const idAttr = dimId ? `id="dim-line-${dimId}" ` : '';
    const groupIdAttr = dimId ? `id="dim-text-group-${dimId}" ` : '';
    const rectIdAttr = dimId ? `id="dim-text-bg-${dimId}" ` : '';
    const textIdAttr = dimId ? `id="dim-text-${dimId}" ` : '';

    return `
      <!-- Extension lines -->
      <line x1="${svgP1.x.toFixed(2)}" y1="${svgP1.y.toFixed(2)}" x2="${svgExt1End.x.toFixed(2)}" y2="${svgExt1End.y.toFixed(2)}" stroke="${COLORS.border}" stroke-width="0.9" stroke-dasharray="3,3" />
      <line x1="${svgP2.x.toFixed(2)}" y1="${svgP2.y.toFixed(2)}" x2="${svgExt2End.x.toFixed(2)}" y2="${svgExt2End.y.toFixed(2)}" stroke="${COLORS.border}" stroke-width="0.9" stroke-dasharray="3,3" />
      <!-- Dimension line with arrows -->
      <line ${idAttr}class="dimension-line" x1="${svgD1.x.toFixed(2)}" y1="${svgD1.y.toFixed(2)}" x2="${svgD2.x.toFixed(2)}" y2="${svgD2.y.toFixed(2)}" stroke="${color}" stroke-width="1.3" marker-start="url(#arr-start-${color.replace('#','')})" marker-end="url(#arr-end-${color.replace('#','')})" />
      <!-- Dimension Text (Strictly Parallel to the Arrow Line) -->
      <g ${groupIdAttr}transform="translate(${midSvg.x.toFixed(2)}, ${midSvg.y.toFixed(2)}) rotate(${angleDeg.toFixed(2)})">
        <rect ${rectIdAttr}class="dimension-text-bg" x="${(-textWidth * 0.5).toFixed(1)}" y="${textOffsetY - 12}" width="${textWidth.toFixed(1)}" height="18" fill="${COLORS.bg}" rx="3" opacity="0.95" />
        <text ${textIdAttr}x="0" y="${textOffsetY}" text-anchor="middle" font-size="13" font-weight="600" fill="${color}">${text}</text>
      </g>
    `;
  }

  // Dimension Bars (ISO 129-1 Stairs)
  const dimPb = makeAlignedDim(A, D, 6.8, tr.fig1_dim_pb, COLORS.dimPb, true, 0, "pb");
  const dimGa = makeAlignedDim(A, E, 13.0, tr.fig1_dim_ga, COLORS.dimGa, true, 82.0, "ga");
  const dimBd = makeAlignedDim(B, D, -8.5, tr.fig1_dim_bd, COLORS.dimBd, false, -15.0, "bd");

  // Label Boxes & Clean Orthogonal Leaders:
  // North Track (Point B and Point D - Placed at Y=82, providing 44px clearance from Title at Y=38)
  const boxB = { id: 'b', x: 300, y: 82, w: 265, h: 32, text: tr.fig1_point_b, color: COLORS.contactLimit };
  const boxD = { id: 'd', x: 730, y: 82, w: 275, h: 32, text: tr.fig1_point_d, color: COLORS.contactLimit };

  // Leader for B: From B box down, bypassing dimGa to X=530, then horizontal to point B with arrow
  const leaderB = `
    <path id="leader-b" class="leader-line" d="M ${(boxB.x + boxB.w * 0.5).toFixed(2)} ${(boxB.y + boxB.h).toFixed(2)} L ${(boxB.x + boxB.w * 0.5).toFixed(2)} 142.00 L 530.00 142.00 L 530.00 ${svgB.y.toFixed(2)} L ${(svgB.x - 7).toFixed(2)} ${svgB.y.toFixed(2)}" fill="none" stroke="${COLORS.contactLimit}" stroke-width="1.2" marker-end="url(#arr-limit)" />
  `;

  // Leader for D: From D box down, bypassing dimGa to X=780, then horizontal to point D with arrow
  const leaderD = `
    <path id="leader-d" class="leader-line" d="M ${(boxD.x + boxD.w * 0.5).toFixed(2)} ${(boxD.y + boxD.h).toFixed(2)} L ${(boxD.x + boxD.w * 0.5).toFixed(2)} 135.00 L 780.00 135.00 L 780.00 ${svgD.y.toFixed(2)} L ${(svgD.x + 7).toFixed(2)} ${svgD.y.toFixed(2)}" fill="none" stroke="${COLORS.contactLimit}" stroke-width="1.2" marker-end="url(#arr-limit)" />
  `;

  // South Track (Point P - Centered closer to pitch line at X=660, Y=430, W=250 for full multilingual clearance)
  // Leader ascends from box center (X=785), navigates safe corridor Y=372 (15px below Point E & leaderE), and vertically indexes Point P
  const boxP = { id: 'p', x: 660, y: 430, w: 250, h: 32, text: tr.fig1_point_p, color: COLORS.pitchPoint };
  const leaderP = `
    <path id="leader-p" class="leader-line" d="M ${(boxP.x + boxP.w * 0.5).toFixed(2)} ${boxP.y.toFixed(2)} L ${(boxP.x + boxP.w * 0.5).toFixed(2)} 372.00 L ${svgP.x.toFixed(2)} 372.00 L ${svgP.x.toFixed(2)} ${(svgP.y + 8).toFixed(2)}" fill="none" stroke="${COLORS.pitchPoint}" stroke-width="1.2" marker-end="url(#arr-pitch-pt)" />
  `;

  // West Track (N1, ra2, A, LOA label)
  const westX = 35;
  const westW = 235;
  const boxLoa = { id: 'loa', x: westX, y: 82, w: 235, h: 32, text: tr.fig1_loa, color: COLORS.actionLine };
  const boxN1 = { id: 'n1', x: westX, y: 155, w: westW, h: 32, text: tr.fig1_point_n1, color: COLORS.basePoint };
  const boxRa2 = { id: 'ra2', x: westX, y: 228, w: westW, h: 32, text: tr.fig1_gear_tip, color: COLORS.gear };
  const boxA = { id: 'a', x: westX, y: 300, w: westW, h: 32, text: tr.fig1_point_a, color: COLORS.contactPoint };

  // Leader for LOA: Clean non-interfering orthogonal corridor between West Track (X<=270) and North Box B (X>=300)
  const leaderLoa = `
    <path id="leader-loa" class="leader-line" d="M ${(boxLoa.x + boxLoa.w).toFixed(2)} ${(boxLoa.y + boxLoa.h * 0.5).toFixed(2)} L 285.00 ${(boxLoa.y + boxLoa.h * 0.5).toFixed(2)} L 285.00 126.00 L ${(svgLoaStart.x - 20).toFixed(2)} 126.00 L ${(svgLoaStart.x - 20).toFixed(2)} ${svgLoaStart.y.toFixed(2)} L ${svgLoaStart.x.toFixed(2)} ${svgLoaStart.y.toFixed(2)}" fill="none" stroke="${COLORS.actionLine}" stroke-width="1.2" marker-end="url(#arr-action)" />
  `;
  const leaderN1 = `
    <path id="leader-n1" class="leader-line" d="M ${(boxN1.x + boxN1.w).toFixed(2)} ${(boxN1.y + boxN1.h * 0.5).toFixed(2)} L ${(svgN1.x - 20).toFixed(2)} ${(boxN1.y + boxN1.h * 0.5).toFixed(2)} L ${(svgN1.x - 20).toFixed(2)} ${svgN1.y.toFixed(2)} L ${(svgN1.x - 7).toFixed(2)} ${svgN1.y.toFixed(2)}" fill="none" stroke="${COLORS.basePoint}" stroke-width="1.2" marker-end="url(#arr-base)" />
  `;
  const ra2ContactX_mm = -14.0;
  const ra2ContactY_mm = -params.r2 + Math.sqrt(params.ra2 * params.ra2 - ra2ContactX_mm * ra2ContactX_mm);
  const ra2ArcPoint = { x: toSvgX(ra2ContactX_mm), y: toSvgY(ra2ContactY_mm) };
  const leaderRa2 = `
    <path id="leader-ra2" class="leader-line" d="M ${(boxRa2.x + boxRa2.w).toFixed(2)} ${(boxRa2.y + boxRa2.h * 0.5).toFixed(2)} L ${(ra2ArcPoint.x - 25).toFixed(2)} ${(boxRa2.y + boxRa2.h * 0.5).toFixed(2)} L ${ra2ArcPoint.x.toFixed(2)} ${ra2ArcPoint.y.toFixed(2)}" fill="none" stroke="${COLORS.gear}" stroke-width="1.2" marker-end="url(#arr-gear)" />
  `;
  const leaderA = `
    <path id="leader-a" class="leader-line" d="M ${(boxA.x + boxA.w).toFixed(2)} ${(boxA.y + boxA.h * 0.5).toFixed(2)} L ${(svgA.x - 20).toFixed(2)} ${(boxA.y + boxA.h * 0.5).toFixed(2)} L ${(svgA.x - 20).toFixed(2)} ${svgA.y.toFixed(2)} L ${(svgA.x - 7).toFixed(2)} ${svgA.y.toFixed(2)}" fill="none" stroke="${COLORS.contactPoint}" stroke-width="1.2" marker-end="url(#arr-contact)" />
  `;

  // East Track (ra1, Pitch Line, E, N2)
  // Shift eastX to 1000, eastW=240 for Part 3 to provide ample room for N2 (x=969)
  const eastX = 1000;
  const eastW = 240;
  const boxRa1 = { id: 'ra1', x: eastX, y: 155, w: eastW, h: 32, text: tr.fig1_pinion_tip, color: COLORS.pinion };
  const boxPitch = { id: 'pitch', x: eastX, y: 228, w: eastW, h: 32, text: tr.fig1_pitch_line, color: COLORS.pitchLine };
  const boxE = { id: 'e', x: eastX, y: 300, w: eastW, h: 32, text: tr.fig1_point_e, color: COLORS.contactPoint };
  const boxN2 = { id: 'n2', x: eastX, y: 372, w: eastW, h: 32, text: tr.fig1_point_n2, color: COLORS.basePoint };

  const ra1ContactX_mm = 14.0;
  const ra1ContactY_mm = params.r1 - Math.sqrt(params.ra1 * params.ra1 - ra1ContactX_mm * ra1ContactX_mm);
  const ra1ArcPoint = { x: toSvgX(ra1ContactX_mm), y: toSvgY(ra1ContactY_mm) };
  const leaderRa1 = `
    <path id="leader-ra1" class="leader-line" d="M ${boxRa1.x.toFixed(2)} ${(boxRa1.y + boxRa1.h * 0.5).toFixed(2)} L ${(ra1ArcPoint.x + 25).toFixed(2)} ${(boxRa1.y + boxRa1.h * 0.5).toFixed(2)} L ${ra1ArcPoint.x.toFixed(2)} ${ra1ArcPoint.y.toFixed(2)}" fill="none" stroke="${COLORS.pinion}" stroke-width="1.2" marker-end="url(#arr-pinion)" />
  `;
  const pitchLineEnd = { x: toSvgX(20.0), y: toSvgY(0.0) };
  const leaderPitch = `
    <path id="leader-pitch" class="leader-line" d="M ${boxPitch.x.toFixed(2)} ${(boxPitch.y + boxPitch.h * 0.5).toFixed(2)} L 925.00 ${(boxPitch.y + boxPitch.h * 0.5).toFixed(2)} L 925.00 ${pitchLineEnd.y.toFixed(2)} L ${(pitchLineEnd.x + 4).toFixed(2)} ${pitchLineEnd.y.toFixed(2)}" fill="none" stroke="${COLORS.pitchLine}" stroke-width="1.2" marker-end="url(#arr-pitch)" />
  `;
  const leaderE = `
    <path id="leader-e" class="leader-line" d="M ${boxE.x.toFixed(2)} ${(boxE.y + boxE.h * 0.5).toFixed(2)} L ${(svgE.x + 20).toFixed(2)} ${(boxE.y + boxE.h * 0.5).toFixed(2)} L ${(svgE.x + 20).toFixed(2)} ${svgE.y.toFixed(2)} L ${(svgE.x + 7).toFixed(2)} ${svgE.y.toFixed(2)}" fill="none" stroke="${COLORS.contactPoint}" stroke-width="1.2" marker-end="url(#arr-contact)" />
  `;
  const leaderN2 = `
    <path id="leader-n2" class="leader-line" d="M ${boxN2.x.toFixed(2)} ${(boxN2.y + boxN2.h * 0.5).toFixed(2)} L ${(svgN2.x + 15).toFixed(2)} ${(boxN2.y + boxN2.h * 0.5).toFixed(2)} L ${(svgN2.x + 15).toFixed(2)} ${svgN2.y.toFixed(2)} L ${(svgN2.x + 7).toFixed(2)} ${svgN2.y.toFixed(2)}" fill="none" stroke="${COLORS.basePoint}" stroke-width="1.2" marker-end="url(#arr-base)" />
  `;

  // Render a clean label box with upgraded typography
  function renderBox(b) {
    const idAttr = b.id ? `id="box-${b.id}" ` : '';
    return `
      <g ${idAttr}class="label-box">
        <rect x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="5" fill="${COLORS.bg}" stroke="${b.color}" stroke-width="1.4" filter="url(#drop-shadow)" />
        <text x="${b.x + b.w * 0.5}" y="${b.y + b.h * 0.5 + 5.0}" text-anchor="middle" font-size="13.5" font-weight="600" fill="${b.color}">${b.text}</text>
      </g>
    `;
  }

  // Summary Card at Bottom
  const cardX = 60;
  const cardY = 510;
  const cardW = 1140;
  const cardH = 360;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${CANVAS_W} ${CANVAS_H}" width="${CANVAS_W}" height="${CANVAS_H}">
  <defs>
    <!-- Drop Shadow Filter -->
    <filter id="drop-shadow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08" />
    </filter>

    <!-- Arrowhead Markers (Strictly zero gap at tip) -->
    <marker id="arr-action" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.actionLine}" />
    </marker>
    <marker id="arr-base" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.basePoint}" />
    </marker>
    <marker id="arr-contact" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.contactPoint}" />
    </marker>
    <marker id="arr-limit" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.contactLimit}" />
    </marker>
    <marker id="arr-pitch" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.pitchLine}" />
    </marker>
    <marker id="arr-pitch-pt" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.pitchPoint}" />
    </marker>
    <marker id="arr-gear" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.gear}" />
    </marker>
    <marker id="arr-pinion" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.pinion}" />
    </marker>

    <!-- Dimension Arrowheads (Double-ended) -->
    <marker id="arr-start-4338ca" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 10 1.5 L 0 5 L 10 8.5 z" fill="${COLORS.dimPb}" />
    </marker>
    <marker id="arr-end-4338ca" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.dimPb}" />
    </marker>
    <marker id="arr-start-ea580c" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 10 1.5 L 0 5 L 10 8.5 z" fill="${COLORS.dimGa}" />
    </marker>
    <marker id="arr-end-ea580c" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.dimGa}" />
    </marker>
    <marker id="arr-start-7c3aed" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 10 1.5 L 0 5 L 10 8.5 z" fill="${COLORS.dimBd}" />
    </marker>
    <marker id="arr-end-7c3aed" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="${COLORS.dimBd}" />
    </marker>

    <style>
      text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", "Noto Sans", sans-serif; }
      .title { font-size: 23px; font-weight: 700; fill: ${COLORS.textMain}; }
      .formula-title { font-size: 18px; font-weight: 700; fill: ${COLORS.textMain}; }
      .formula-text { font-size: 15px; font-weight: 500; fill: ${COLORS.textSub}; }
      .formula-highlight { font-size: 15px; font-weight: 600; fill: ${COLORS.actionLine}; }
      .formula-note { font-size: 14.5px; font-weight: 600; fill: ${COLORS.contactPoint}; }
      .formula-params { font-size: 13px; font-weight: 500; fill: ${COLORS.textSub}; }
    </style>
  </defs>

  <rect width="${CANVAS_W}" height="${CANVAS_H}" fill="${COLORS.bg}" />

  <!-- Diagram Title (Comfortable Y=38) -->
  <text x="${CANVAS_W * 0.5}" y="38" text-anchor="middle" class="title">${tr.fig1_title}</text>

  <!-- 1. Centerline & Pitch Tangent -->
  <line x1="${toSvgX(0)}" y1="${toSvgY(-9.0)}" x2="${toSvgX(0)}" y2="${toSvgY(9.0)}" stroke="${COLORS.axisLine}" stroke-width="1.0" stroke-dasharray="8,4,2,4" />
  <line x1="${toSvgX(-28.0)}" y1="${toSvgY(0)}" x2="${toSvgX(20.0)}" y2="${toSvgY(0)}" stroke="${COLORS.pitchLine}" stroke-width="1.2" stroke-dasharray="6,4" />

  <!-- 2. Pitch Circles -->
  <path d="${arcPath(svgO1, params.r1, 255, 285)}" fill="none" stroke="${COLORS.pitchLine}" stroke-width="1.1" stroke-dasharray="4,3" opacity="0.85" />
  <path d="${arcPath(svgO2, params.r2, 75, 105)}" fill="none" stroke="${COLORS.pitchLine}" stroke-width="1.1" stroke-dasharray="4,3" opacity="0.85" />

  <!-- 3. Tip Circles (ra1, ra2) -->
  <path d="${arcPath(svgO1, params.ra1, 250, 290)}" fill="none" stroke="${COLORS.pinion}" stroke-width="1.8" />
  <path d="${arcPath(svgO2, params.ra2, 70, 110)}" fill="none" stroke="${COLORS.gear}" stroke-width="1.8" />

  <!-- 4. Line of Action (Extended segment) -->
  <line x1="${svgLoaStart.x.toFixed(2)}" y1="${svgLoaStart.y.toFixed(2)}" x2="${svgLoaEnd.x.toFixed(2)}" y2="${svgLoaEnd.y.toFixed(2)}" stroke="${COLORS.actionLine}" stroke-width="1.6" />

  <!-- 5. Active Contact Bands -->
  <!-- Full Active Path AE -->
  <line x1="${svgA.x.toFixed(2)}" y1="${svgA.y.toFixed(2)}" x2="${svgE.x.toFixed(2)}" y2="${svgE.y.toFixed(2)}" stroke="${COLORS.bandActive}" stroke-width="7.5" stroke-linecap="round" />
  <!-- Single Contact Path BD -->
  <line x1="${svgB.x.toFixed(2)}" y1="${svgB.y.toFixed(2)}" x2="${svgD.x.toFixed(2)}" y2="${svgD.y.toFixed(2)}" stroke="${COLORS.bandSingle}" stroke-width="6.0" stroke-linecap="round" />

  <!-- 6. Landmark Points -->
  <!-- N1 (T1) Square -->
  <rect x="${(svgN1.x - 4.5).toFixed(2)}" y="${(svgN1.y - 4.5).toFixed(2)}" width="9" height="9" fill="${COLORS.basePoint}" stroke="#ffffff" stroke-width="1.2" />
  <!-- A Circle -->
  <circle cx="${svgA.x.toFixed(2)}" cy="${svgA.y.toFixed(2)}" r="5.5" fill="${COLORS.contactPoint}" stroke="#ffffff" stroke-width="1.5" />
  <!-- B Circle -->
  <circle cx="${svgB.x.toFixed(2)}" cy="${svgB.y.toFixed(2)}" r="5.5" fill="${COLORS.contactLimit}" stroke="#ffffff" stroke-width="1.5" />
  <!-- P Circle (Pitch Point) -->
  <circle cx="${svgP.x.toFixed(2)}" cy="${svgP.y.toFixed(2)}" r="6.5" fill="${COLORS.pitchPoint}" stroke="#ffffff" stroke-width="1.8" />
  <!-- D Circle -->
  <circle cx="${svgD.x.toFixed(2)}" cy="${svgD.y.toFixed(2)}" r="5.5" fill="${COLORS.contactLimit}" stroke="#ffffff" stroke-width="1.5" />
  <!-- E Circle -->
  <circle cx="${svgE.x.toFixed(2)}" cy="${svgE.y.toFixed(2)}" r="5.5" fill="${COLORS.contactPoint}" stroke="#ffffff" stroke-width="1.5" />
  <!-- N2 (T2) Square -->
  <rect x="${(svgN2.x - 4.5).toFixed(2)}" y="${(svgN2.y - 4.5).toFixed(2)}" width="9" height="9" fill="${COLORS.basePoint}" stroke="#ffffff" stroke-width="1.2" />

  <!-- 7. Orthogonal Leader Lines (Zero Intersect) -->
  ${leaderLoa}
  ${leaderN1}
  ${leaderRa2}
  ${leaderA}
  ${leaderB}
  ${leaderD}
  ${leaderP}
  ${leaderRa1}
  ${leaderPitch}
  ${leaderE}
  ${leaderN2}

  <!-- 8. Dimensions (Strictly Parallel along LOA) -->
  ${dimPb}
  ${dimGa}
  ${dimBd}

  <!-- 9. Label Boxes -->
  ${renderBox(boxLoa)}
  ${renderBox(boxN1)}
  ${renderBox(boxRa2)}
  ${renderBox(boxA)}
  
  ${renderBox(boxB)}
  ${renderBox(boxD)}
  
  ${renderBox(boxP)}
  
  ${renderBox(boxRa1)}
  ${renderBox(boxPitch)}
  ${renderBox(boxE)}
  ${renderBox(boxN2)}

  <!-- 10. Summary Formula Card -->
  <g class="summary-card" filter="url(#drop-shadow)">
    <rect x="${cardX}" y="${cardY}" width="${cardW}" height="${cardH}" rx="8" fill="${COLORS.cardBg}" stroke="${COLORS.cardBorder}" stroke-width="1.3" />
    
    <!-- Header -->
    <text x="${cardX + cardW * 0.5}" y="${cardY + 38}" text-anchor="middle" class="formula-title">${tr.summary_card_title}</text>
    <line x1="${cardX + 40}" y1="${cardY + 56}" x2="${cardX + cardW - 40}" y2="${cardY + 56}" stroke="${COLORS.border}" stroke-width="0.9" />
    
    <!-- Formulas -->
    <text x="${cardX + 60}" y="${cardY + 104}" class="formula-text">${tr.summary_formula_1}</text>
    <text x="${cardX + 60}" y="${cardY + 158}" class="formula-text">${tr.summary_formula_2}</text>
    <text x="${cardX + 60}" y="${cardY + 212}" class="formula-text">${tr.summary_formula_3}</text>
    
    <line x1="${cardX + 40}" y1="${cardY + 250}" x2="${cardX + cardW - 40}" y2="${cardY + 250}" stroke="${COLORS.border}" stroke-width="0.9" />
    
    <!-- Engineering Note -->
    <text x="${cardX + cardW * 0.5}" y="${cardY + 288}" text-anchor="middle" class="formula-note">${tr.summary_formula_note}</text>
    <text x="${cardX + cardW * 0.5}" y="${cardY + 324}" text-anchor="middle" class="formula-params">${tr.summary_params_header} m = 3.0 mm, z₁ = 18, z₂ = 54, α₀ = 20.0°, a = 108.0 mm (ISO 21771 / DIN 3960 Closed-Form)</text>
  </g>
</svg>
`;
}

/**
 * Main render function across all 4 languages.
 */
async function main() {
  const languages = ['ko', 'en', 'de', 'ja'];
  
  for (const lang of languages) {
    const svgStr = generateSvgForLanguage(lang);
    const langOutDir = path.join(PUBLIC_IMG_DIR, lang);
    fs.mkdirSync(langOutDir, { recursive: true });

    const svgFile = path.join(langOutDir, 'fig1_line_of_action_five_points.svg');
    const pngFile = path.join(langOutDir, 'fig1_line_of_action_five_points.png');

    // 1. Write clean SVG
    fs.writeFileSync(svgFile, svgStr, 'utf-8');

    // 2. Export 300 DPI PNG via sharp
    // 1260 x 920 at density 300 (4.166x scale) -> 5250 x 3833 px
    await sharp(Buffer.from(svgStr), { density: 300 })
      .png({ compressionLevel: 9 })
      .toFile(pngFile);

    const svgSize = (fs.statSync(svgFile).size / 1024).toFixed(1);
    const pngSize = (fs.statSync(pngFile).size / 1024).toFixed(1);
    console.log(`[PASS] ${lang.toUpperCase()}: SVG (${svgSize} KB) -> PNG (${pngSize} KB)`);
  }

  console.log('\n[SUCCESS] Part 3 Fig 1 successfully rendered across 4 languages with high-precision vector routing.');
}

main().catch(err => {
  console.error('[ERROR] Rendering failed:', err);
  process.exit(1);
});
