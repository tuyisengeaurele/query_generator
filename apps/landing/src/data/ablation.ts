// Mirrors eval/results/ablation.md. Update this file by hand after running
// eval/ablation.py; there is no build-time step that reads the markdown
// report automatically. Set `available: true` once real numbers exist,
// rather than showing a fabricated accuracy figure.
export interface AblationResult {
  available: boolean;
  totalQuestions: number;
  correctionDisabledAccuracy: number | null;
  correctionEnabledAccuracy: number | null;
  runDate: string | null;
}

export const ablationResult: AblationResult = {
  available: false,
  totalQuestions: 40,
  correctionDisabledAccuracy: null,
  correctionEnabledAccuracy: null,
  runDate: null,
};
