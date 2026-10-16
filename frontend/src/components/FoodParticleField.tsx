import { useEffect, useRef } from "react";

/** Transparent cell */
const T = "";

type PixelMap = string[][];

const SPRITES: PixelMap[] = [
  // egg
  [
    [T, T, T, T, "#f5e6c8", "#f5e6c8", "#f5e6c8", "#f5e6c8", T, T, T, T, T, T, T, T],
    [T, T, T, "#f5e6c8", "#fff8e7", "#fff8e7", "#fff8e7", "#fff8e7", "#f5e6c8", T, T, T, T, T, T, T],
    [T, T, "#f5e6c8", "#fff8e7", "#fff8e7", "#fff8e7", "#fff8e7", "#fff8e7", "#fff8e7", "#f5e6c8", T, T, T, T, T, T],
    [T, "#f5e6c8", "#fff8e7", "#fff8e7", "#fff8e7", "#ffd54a", "#ffd54a", "#fff8e7", "#fff8e7", "#fff8e7", "#f5e6c8", T, T, T, T, T],
    [T, "#f5e6c8", "#fff8e7", "#fff8e7", "#ffd54a", "#ffb300", "#ffb300", "#ffd54a", "#fff8e7", "#fff8e7", "#f5e6c8", T, T, T, T, T],
    [T, "#f5e6c8", "#fff8e7", "#fff8e7", "#ffd54a", "#ffb300", "#ffb300", "#ffd54a", "#fff8e7", "#fff8e7", "#f5e6c8", T, T, T, T, T],
    [T, T, "#f5e6c8", "#fff8e7", "#fff8e7", "#ffd54a", "#ffd54a", "#fff8e7", "#fff8e7", "#f5e6c8", T, T, T, T, T, T],
    [T, T, T, "#f5e6c8", "#fff8e7", "#fff8e7", "#fff8e7", "#fff8e7", "#f5e6c8", T, T, T, T, T, T, T],
    [T, T, T, T, "#f5e6c8", "#f5e6c8", "#f5e6c8", "#f5e6c8", T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
  ],
  // broccoli
  [
    [T, T, T, "#2e7d32", "#43a047", "#2e7d32", T, T, T, T, T, T, T, T, T, T],
    [T, T, "#43a047", "#66bb6a", "#43a047", "#66bb6a", "#2e7d32", T, T, T, T, T, T, T, T, T],
    [T, "#2e7d32", "#66bb6a", "#a5d6a7", "#66bb6a", "#a5d6a7", "#43a047", "#2e7d32", T, T, T, T, T, T, T, T],
    [T, "#43a047", "#66bb6a", "#66bb6a", "#43a047", "#66bb6a", "#66bb6a", "#43a047", T, T, T, T, T, T, T, T],
    [T, T, "#2e7d32", "#43a047", "#8d6e63", "#43a047", "#2e7d32", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#8d6e63", "#6d4c41", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#6d4c41", "#5d4037", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#5d4037", T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
  ],
  // bread
  [
    [T, T, "#c62828", "#d84315", "#ef6c00", "#d84315", "#c62828", T, T, T, T, T, T, T, T, T],
    [T, "#d84315", "#ffcc80", "#ffe0b2", "#ffcc80", "#ffe0b2", "#ffcc80", "#d84315", T, T, T, T, T, T, T, T],
    ["#ef6c00", "#ffcc80", "#ffe0b2", "#fff3e0", "#ffe0b2", "#fff3e0", "#ffe0b2", "#ffcc80", "#ef6c00", T, T, T, T, T, T, T],
    ["#d84315", "#ffcc80", "#ffe0b2", "#ffe0b2", "#ffcc80", "#ffe0b2", "#ffe0b2", "#ffcc80", "#d84315", T, T, T, T, T, T, T],
    ["#c62828", "#ef6c00", "#ffcc80", "#ffcc80", "#ef6c00", "#ffcc80", "#ffcc80", "#ef6c00", "#c62828", T, T, T, T, T, T, T],
    [T, "#c62828", "#d84315", "#ef6c00", "#d84315", "#ef6c00", "#d84315", "#c62828", T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
  ],
  // apple
  [
    [T, T, T, T, T, "#5d4037", "#2e7d32", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#c62828", "#e53935", "#5d4037", "#43a047", T, T, T, T, T, T, T, T],
    [T, T, T, "#e53935", "#ef5350", "#ff8a80", "#e53935", "#c62828", T, T, T, T, T, T, T, T],
    [T, T, "#c62828", "#ef5350", "#ff8a80", "#ef5350", "#ef5350", "#e53935", "#c62828", T, T, T, T, T, T, T],
    [T, T, "#b71c1c", "#e53935", "#ef5350", "#e53935", "#e53935", "#c62828", "#b71c1c", T, T, T, T, T, T, T],
    [T, T, T, "#b71c1c", "#c62828", "#c62828", "#c62828", "#b71c1c", T, T, T, T, T, T, T, T],
    [T, T, T, T, "#880e4f", "#b71c1c", "#880e4f", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
  ],
  // chicken drumstick
  [
    [T, T, T, T, T, "#ffe0b2", "#ffcc80", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#ffcc80", "#ffab91", "#ffcc80", "#ffe0b2", T, T, T, T, T, T, T, T],
    [T, T, T, "#ffab91", "#ff8a65", "#ffab91", "#ffcc80", "#ffab91", T, T, T, T, T, T, T, T],
    [T, T, "#ff8a65", "#ff7043", "#ff8a65", "#ffab91", "#ff8a65", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#bf360c", "#e64a19", "#ff7043", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#eceff1", "#cfd8dc", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#cfd8dc", "#b0bec5", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#90a4ae", T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
  ],
  // carrot
  [
    [T, T, T, T, "#2e7d32", "#43a047", "#2e7d32", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#ef6c00", "#ff9800", "#ef6c00", "#ff9800", "#e65100", T, T, T, T, T, T, T, T],
    [T, T, T, T, "#ff9800", "#ffb74d", "#ff9800", "#ef6c00", T, T, T, T, T, T, T, T],
    [T, T, T, T, "#ef6c00", "#ff9800", "#ef6c00", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, "#e65100", "#ef6c00", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, "#bf360c", "#e65100", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, "#bf360c", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
  ],
  // fish
  [
    [T, T, T, T, "#4fc3f7", "#29b6f6", "#0288d1", T, T, T, T, T, T, T, T, T],
    [T, T, "#81d4fa", "#4fc3f7", "#29b6f6", "#4fc3f7", "#29b6f6", "#0277bd", T, T, T, T, T, T, T, T],
    [T, "#4fc3f7", "#e1f5fe", "#4fc3f7", "#29b6f6", "#01579b", "#29b6f6", "#0288d1", "#01579b", T, T, T, T, T, T, T],
    [T, T, "#29b6f6", "#4fc3f7", "#0288d1", "#29b6f6", "#0288d1", "#01579b", T, T, T, T, T, T, T, T],
    [T, T, T, "#0277bd", "#0288d1", "#01579b", "#0277bd", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
  ],
  // cheese
  [
    [T, T, "#f9a825", "#fbc02d", "#f9a825", "#fbc02d", "#f9a825", T, T, T, T, T, T, T, T, T],
    [T, "#fbc02d", "#ffeb3b", "#fff176", "#ffeb3b", "#fdd835", "#ffeb3b", "#f9a825", T, T, T, T, T, T, T, T],
    ["#f9a825", "#ffeb3b", "#fff59d", "#ffeb3b", "#fdd835", "#ffeb3b", "#fff176", "#fbc02d", "#f57f17", T, T, T, T, T, T, T],
    ["#f57f17", "#fbc02d", "#ffeb3b", "#fdd835", "#ffeb3b", "#fbc02d", "#ffeb3b", "#f9a825", "#f57f17", T, T, T, T, T, T, T],
    [T, "#f57f17", "#f9a825", "#fbc02d", "#f9a825", "#fbc02d", "#f9a825", "#f57f17", T, T, T, T, T, T, T, T],
  ],
  // banana
  [
    [T, T, T, T, T, "#fdd835", "#fbc02d", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#fdd835", "#ffee58", "#fdd835", "#f9a825", T, T, T, T, T, T, T, T],
    [T, T, T, "#fbc02d", "#ffee58", "#fff59d", "#ffee58", "#fdd835", T, T, T, T, T, T, T, T],
    [T, T, "#f9a825", "#fdd835", "#ffee58", "#fdd835", "#fbc02d", T, T, T, T, T, T, T, T, T],
    [T, "#f57f17", "#f9a825", "#fbc02d", "#fdd835", "#f9a825", T, T, T, T, T, T, T, T, T, T],
    [T, T, "#6d4c41", "#f57f17", "#f9a825", T, T, T, T, T, T, T, T, T, T, T],
  ],
  // strawberry
  [
    [T, T, T, T, "#2e7d32", "#43a047", "#2e7d32", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#e53935", "#ef5350", "#e53935", "#ef5350", "#c62828", T, T, T, T, T, T, T, T],
    [T, T, "#c62828", "#ef5350", "#ff8a80", "#ef5350", "#ff8a80", "#e53935", "#b71c1c", T, T, T, T, T, T, T],
    [T, T, "#b71c1c", "#e53935", "#ef5350", "#e53935", "#ef5350", "#c62828", "#880e4f", T, T, T, T, T, T, T],
    [T, T, T, "#880e4f", "#c62828", "#b71c1c", "#c62828", "#880e4f", T, T, T, T, T, T, T, T],
  ],
  // grapes
  [
    [T, T, T, "#6a1b9a", "#8e24aa", "#6a1b9a", T, T, T, T, T, T, T, T, T, T],
    [T, T, "#8e24aa", "#ab47bc", "#8e24aa", "#ab47bc", "#6a1b9a", T, T, T, T, T, T, T, T, T],
    [T, "#6a1b9a", "#ab47bc", "#ce93d8", "#ab47bc", "#ce93d8", "#8e24aa", "#4a148c", T, T, T, T, T, T, T, T],
    [T, T, "#4a148c", "#8e24aa", "#ab47bc", "#8e24aa", "#6a1b9a", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#4a148c", "#6a1b9a", "#4a148c", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#2e7d32", T, T, T, T, T, T, T, T, T, T, T],
  ],
  // lemon
  [
    [T, T, T, "#fbc02d", "#fdd835", "#fbc02d", "#fdd835", T, T, T, T, T, T, T, T, T],
    [T, T, "#f9a825", "#ffee58", "#fff59d", "#ffee58", "#fdd835", "#f9a825", T, T, T, T, T, T, T, T],
    [T, "#f57f17", "#fdd835", "#fff59d", "#ffee58", "#fff59d", "#fdd835", "#fbc02d", T, T, T, T, T, T, T, T],
    [T, T, "#f9a825", "#fdd835", "#ffee58", "#fdd835", "#fbc02d", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#f57f17", "#f9a825", "#f57f17", T, T, T, T, T, T, T, T, T, T],
  ],
  // orange
  [
    [T, T, T, "#ef6c00", "#ff9800", "#ef6c00", "#ff9800", T, T, T, T, T, T, T, T, T],
    [T, T, "#e65100", "#ffb74d", "#ffe0b2", "#ffb74d", "#ff9800", "#e65100", T, T, T, T, T, T, T, T],
    [T, "#bf360c", "#ff9800", "#ffe0b2", "#ffb74d", "#ffe0b2", "#ff9800", "#ef6c00", T, T, T, T, T, T, T, T],
    [T, T, "#e65100", "#ff9800", "#ffb74d", "#ff9800", "#ef6c00", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#bf360c", "#e65100", "#bf360c", T, T, T, T, T, T, T, T, T, T],
  ],
  // watermelon wedge
  [
    [T, T, T, T, T, "#c62828", "#e53935", "#c62828", T, T, T, T, T, T, T, T],
    [T, T, T, T, "#e53935", "#ef5350", "#ff8a80", "#ef5350", "#2e7d32", T, T, T, T, T, T, T],
    [T, T, T, "#c62828", "#ef5350", "#ffcdd2", "#ef5350", "#e53935", "#43a047", "#1b5e20", T, T, T, T, T],
    [T, T, "#b71c1c", "#e53935", "#ef5350", "#e53935", "#c62828", "#2e7d32", "#1b5e20", T, T, T, T, T, T, T],
    [T, T, T, "#880e4f", "#b71c1c", "#880e4f", "#1b5e20", T, T, T, T, T, T, T, T, T],
  ],
  // cherries
  [
    [T, T, T, T, T, "#2e7d32", "#5d4037", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#c62828", "#e53935", T, "#5d4037", "#e53935", "#c62828", T, T, T, T, T, T, T],
    [T, T, "#b71c1c", "#ef5350", "#c62828", T, T, "#c62828", "#ef5350", "#b71c1c", T, T, T, T, T, T],
    [T, T, T, "#880e4f", "#b71c1c", T, T, "#b71c1c", "#880e4f", T, T, T, T, T, T, T],
  ],
  // pear
  [
    [T, T, T, T, T, "#558b2f", "#2e7d32", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#9ccc65", "#aed581", "#9ccc65", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#7cb342", "#c5e1a5", "#dcedc8", "#c5e1a5", "#7cb342", T, T, T, T, T, T, T, T],
    [T, T, "#558b2f", "#9ccc65", "#c5e1a5", "#9ccc65", "#aed581", "#558b2f", T, T, T, T, T, T, T, T],
    [T, T, T, "#33691e", "#7cb342", "#558b2f", "#33691e", T, T, T, T, T, T, T, T, T],
  ],
  // tomato
  [
    [T, T, T, T, "#2e7d32", "#43a047", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, "#e53935", "#ef5350", "#e53935", "#ef5350", T, T, T, T, T, T, T, T, T],
    [T, T, "#c62828", "#ef5350", "#ff8a80", "#ef5350", "#ff8a80", "#c62828", T, T, T, T, T, T, T, T],
    [T, T, "#b71c1c", "#e53935", "#ef5350", "#e53935", "#c62828", "#b71c1c", T, T, T, T, T, T, T, T],
    [T, T, T, "#880e4f", "#b71c1c", "#880e4f", T, T, T, T, T, T, T, T, T, T],
  ],
  // corn
  [
    [T, T, T, "#fdd835", "#fbc02d", "#fdd835", "#fbc02d", T, T, T, T, T, T, T, T, T],
    [T, T, "#f9a825", "#ffee58", "#fdd835", "#ffee58", "#fdd835", "#f9a825", T, T, T, T, T, T, T, T],
    [T, T, "#f57f17", "#fdd835", "#ffee58", "#fdd835", "#ffee58", "#fbc02d", T, T, T, T, T, T, T, T],
    [T, T, "#2e7d32", "#f9a825", "#fdd835", "#f9a825", "#fbc02d", "#43a047", T, T, T, T, T, T, T, T],
    [T, T, T, "#1b5e20", "#2e7d32", "#1b5e20", T, T, T, T, T, T, T, T, T, T],
  ],
  // mushroom
  [
    [T, T, T, "#c62828", "#e53935", "#ef5350", "#e53935", "#c62828", T, T, T, T, T, T, T, T],
    [T, T, "#b71c1c", "#ef5350", "#ffcdd2", "#ef5350", "#ffcdd2", "#e53935", "#b71c1c", T, T, T, T, T, T, T],
    [T, T, T, "#b71c1c", "#e53935", "#c62828", "#e53935", "#b71c1c", T, T, T, T, T, T, T, T],
    [T, T, T, T, "#efebe9", "#d7ccc8", "#efebe9", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#d7ccc8", "#bcaaa4", "#d7ccc8", T, T, T, T, T, T, T, T, T],
  ],
  // eggplant
  [
    [T, T, T, T, "#2e7d32", "#43a047", T, T, T, T, T, T, T, T, T, T],
    [T, T, T, "#6a1b9a", "#8e24aa", "#6a1b9a", "#8e24aa", T, T, T, T, T, T, T, T, T],
    [T, T, "#4a148c", "#8e24aa", "#ce93d8", "#8e24aa", "#ab47bc", "#4a148c", T, T, T, T, T, T, T, T],
    [T, T, "#4a148c", "#6a1b9a", "#8e24aa", "#6a1b9a", "#4a148c", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#311b92", "#4a148c", "#311b92", T, T, T, T, T, T, T, T, T, T],
  ],
  // bell pepper
  [
    [T, T, T, T, "#1b5e20", "#2e7d32", T, T, T, T, T, T, T, T, T, T],
    [T, T, "#2e7d32", "#43a047", "#66bb6a", "#43a047", "#66bb6a", "#2e7d32", T, T, T, T, T, T, T, T],
    [T, "#1b5e20", "#66bb6a", "#a5d6a7", "#66bb6a", "#a5d6a7", "#43a047", "#1b5e20", T, T, T, T, T, T, T, T],
    [T, T, "#1b5e20", "#43a047", "#66bb6a", "#43a047", "#2e7d32", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#0d3b16", "#1b5e20", "#0d3b16", T, T, T, T, T, T, T, T, T, T],
  ],
  // potato
  [
    [T, T, T, "#8d6e63", "#a1887f", "#8d6e63", "#a1887f", T, T, T, T, T, T, T, T, T],
    [T, T, "#6d4c41", "#bcaaa4", "#d7ccc8", "#bcaaa4", "#a1887f", "#6d4c41", T, T, T, T, T, T, T, T],
    [T, T, "#5d4037", "#a1887f", "#bcaaa4", "#a1887f", "#8d6e63", "#5d4037", T, T, T, T, T, T, T, T],
    [T, T, T, "#5d4037", "#8d6e63", "#5d4037", T, T, T, T, T, T, T, T, T, T],
  ],
  // pizza slice
  [
    [T, T, T, T, T, "#ffcc80", "#ffe0b2", "#ffcc80", T, T, T, T, T, T, T, T],
    [T, T, T, T, "#ef6c00", "#ff8a65", "#ef6c00", "#ff8a65", "#e65100", T, T, T, T, T, T, T],
    [T, T, T, "#e65100", "#fff59d", "#c62828", "#fff59d", "#43a047", "#ffcc80", "#bf360c", T, T, T, T, T, T],
    [T, T, "#bf360c", "#ffcc80", "#fff59d", "#fff59d", "#c62828", "#fff59d", "#ffcc80", "#e65100", T, T, T, T, T, T],
    [T, T, T, "#8d6e63", "#bf360c", "#e65100", "#bf360c", "#8d6e63", T, T, T, T, T, T, T, T],
  ],
  // donut
  [
    [T, T, T, "#f8bbd0", "#f48fb1", "#f8bbd0", "#f48fb1", T, T, T, T, T, T, T, T, T],
    [T, T, "#f48fb1", "#fce4ec", "#42a5f5", "#fce4ec", "#66bb6a", "#f48fb1", T, T, T, T, T, T, T, T],
    [T, "#ec407a", "#fce4ec", "#ffe082", T, T, "#fce4ec", "#ff7043", "#ec407a", T, T, T, T, T, T, T],
    [T, T, "#ad1457", "#f48fb1", "#fce4ec", "#f48fb1", "#f8bbd0", "#ad1457", T, T, T, T, T, T, T, T],
    [T, T, T, "#880e4f", "#ad1457", "#880e4f", T, T, T, T, T, T, T, T, T, T],
  ],
  // fries
  [
    [T, T, "#ef6c00", "#ff9800", "#fdd835", "#ff9800", "#ef6c00", T, T, T, T, T, T, T, T, T],
    [T, "#e65100", "#ffb74d", "#ffee58", "#ffb74d", "#ffee58", "#ffb74d", "#e65100", T, T, T, T, T, T, T, T],
    [T, "#bf360c", "#ff9800", "#fdd835", "#ff9800", "#fdd835", "#ff9800", "#bf360c", T, T, T, T, T, T, T, T],
    [T, "#c62828", "#e53935", "#c62828", "#e53935", "#c62828", "#e53935", "#c62828", T, T, T, T, T, T, T, T],
    [T, T, "#b71c1c", "#c62828", "#b71c1c", "#c62828", "#b71c1c", T, T, T, T, T, T, T, T, T],
  ],
  // popcorn
  [
    [T, T, "#fff59d", "#ffee58", "#fff59d", T, T, T, T, T, T, T, T, T, T, T],
    [T, "#ffee58", "#fffde7", "#ffee58", "#fffde7", "#ffee58", T, T, T, T, T, T, T, T, T, T],
    [T, "#c62828", "#ffffff", "#c62828", "#ffffff", "#c62828", "#ffffff", "#c62828", T, T, T, T, T, T, T, T],
    [T, "#b71c1c", "#ffffff", "#b71c1c", "#ffffff", "#b71c1c", "#ffffff", "#b71c1c", T, T, T, T, T, T, T, T],
    [T, T, "#880e4f", "#b71c1c", "#880e4f", "#b71c1c", "#880e4f", T, T, T, T, T, T, T, T, T],
  ],
  // cookie
  [
    [T, T, T, "#8d6e63", "#a1887f", "#8d6e63", "#a1887f", T, T, T, T, T, T, T, T, T],
    [T, T, "#6d4c41", "#bcaaa4", "#5d4037", "#d7ccc8", "#5d4037", "#6d4c41", T, T, T, T, T, T, T, T],
    [T, "#5d4037", "#a1887f", "#d7ccc8", "#a1887f", "#5d4037", "#bcaaa4", "#8d6e63", "#5d4037", T, T, T, T, T, T, T],
    [T, T, "#4e342e", "#8d6e63", "#a1887f", "#8d6e63", "#6d4c41", "#4e342e", T, T, T, T, T, T, T, T],
    [T, T, T, "#3e2723", "#4e342e", "#3e2723", T, T, T, T, T, T, T, T, T, T],
  ],
  // ice cream
  [
    [T, T, T, T, "#f8bbd0", "#fce4ec", "#f8bbd0", T, T, T, T, T, T, T, T, T],
    [T, T, T, "#f48fb1", "#ffffff", "#f48fb1", "#ffffff", "#f48fb1", T, T, T, T, T, T, T, T],
    [T, T, T, T, "#f48fb1", "#f8bbd0", "#f48fb1", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, "#ffcc80", "#ffe0b2", "#ffcc80", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, "#ef6c00", "#ffcc80", T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, "#e65100", T, T, T, T, T, T, T, T, T],
  ],
  // chips bag
  [
    [T, T, "#fbc02d", "#fdd835", "#fbc02d", "#fdd835", "#fbc02d", T, T, T, T, T, T, T, T, T],
    [T, "#f57f17", "#ffee58", "#e53935", "#ffee58", "#e53935", "#ffee58", "#f57f17", T, T, T, T, T, T, T, T],
    [T, "#ef6c00", "#fdd835", "#ffee58", "#fdd835", "#ffee58", "#fdd835", "#ef6c00", T, T, T, T, T, T, T, T],
    [T, "#e65100", "#fbc02d", "#fdd835", "#fbc02d", "#fdd835", "#fbc02d", "#e65100", T, T, T, T, T, T, T, T],
    [T, T, "#bf360c", "#e65100", "#bf360c", "#e65100", "#bf360c", T, T, T, T, T, T, T, T, T],
  ],
  // pretzel
  [
    [T, T, T, "#8d6e63", "#a1887f", "#8d6e63", T, T, T, T, T, T, T, T, T, T],
    [T, T, "#6d4c41", "#bcaaa4", T, T, "#bcaaa4", "#6d4c41", T, T, T, T, T, T, T, T],
    [T, "#5d4037", "#a1887f", T, "#8d6e63", "#a1887f", T, "#a1887f", "#5d4037", T, T, T, T, T, T, T],
    [T, T, "#6d4c41", "#bcaaa4", "#8d6e63", "#bcaaa4", "#a1887f", "#6d4c41", T, T, T, T, T, T, T, T],
    [T, T, T, "#5d4037", "#6d4c41", "#5d4037", T, T, T, T, T, T, T, T, T, T],
  ],
];

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  spriteIndex: number;
  phase: number;
  spin: number;
  angle: number;
}

const PARTICLE_COUNT = 55;

function bakeSprites(): HTMLCanvasElement[] {
  return SPRITES.map((map) => {
    const c = document.createElement("canvas");
    c.width = 16;
    c.height = 16;
    const ctx = c.getContext("2d")!;
    for (let y = 0; y < 16; y++) {
      const row = map[y] ?? [];
      for (let x = 0; x < 16; x++) {
        const color = row[x];
        if (!color) continue;
        ctx.fillStyle = color;
        ctx.fillRect(x, y, 1, 1);
      }
    }
    return c;
  });
}

function spawnParticle(w: number, h: number): Particle {
  const speed = 0.15 + Math.random() * 0.35;
  const dir = Math.random() * Math.PI * 2;
  return {
    x: Math.random() * w,
    y: Math.random() * h,
    vx: Math.cos(dir) * speed,
    vy: Math.sin(dir) * speed,
    size: 28 + Math.random() * 36,
    spriteIndex: Math.floor(Math.random() * SPRITES.length),
    phase: Math.random() * Math.PI * 2,
    spin: (Math.random() - 0.5) * 0.008,
    angle: Math.random() * Math.PI * 2,
  };
}

export default function FoodParticleField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const sprites = bakeSprites();
    let particles: Particle[] = [];
    let raf = 0;
    let running = true;
    let width = 0;
    let height = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (particles.length === 0) {
        particles = Array.from({ length: PARTICLE_COUNT }, () => spawnParticle(width, height));
      }
    };

    const drawBackground = () => {
      const g = ctx.createLinearGradient(0, 0, 0, height);
      g.addColorStop(0, "#dff4ff");
      g.addColorStop(0.45, "#c5ebff");
      g.addColorStop(1, "#eaf8ff");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, width, height);

      const glow = ctx.createRadialGradient(width * 0.5, height * 0.2, 0, width * 0.5, height * 0.2, width * 0.55);
      glow.addColorStop(0, "rgba(0, 168, 255, 0.22)");
      glow.addColorStop(1, "rgba(0, 168, 255, 0)");
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, width, height);
    };

    const drawParticle = (p: Particle, bob = 0) => {
      const sprite = sprites[p.spriteIndex];
      ctx.save();
      ctx.translate(p.x, p.y + bob);
      ctx.rotate(p.angle);
      ctx.imageSmoothingEnabled = false;
      ctx.globalAlpha = 0.88;
      ctx.drawImage(sprite, -p.size / 2, -p.size / 2, p.size, p.size);
      ctx.restore();
    };

    const paintStatic = () => {
      drawBackground();
      for (const p of particles) drawParticle(p);
    };

    const tick = (t: number) => {
      if (!running) return;
      drawBackground();
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        p.angle += p.spin;
        const bob = Math.sin(t * 0.0015 + p.phase) * 6;

        const margin = p.size;
        if (p.x < -margin) p.x = width + margin;
        if (p.x > width + margin) p.x = -margin;
        if (p.y < -margin) p.y = height + margin;
        if (p.y > height + margin) p.y = -margin;

        drawParticle(p, bob);
      }
      raf = requestAnimationFrame(tick);
    };

    const onVisibility = () => {
      if (document.hidden) {
        running = false;
        cancelAnimationFrame(raf);
      } else if (!reducedMotion) {
        running = true;
        raf = requestAnimationFrame(tick);
      }
    };

    resize();
    if (reducedMotion) {
      paintStatic();
    } else {
      raf = requestAnimationFrame(tick);
    }

    window.addEventListener("resize", resize);
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      running = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, []);

  return <canvas ref={canvasRef} className="particle-canvas" aria-hidden />;
}
