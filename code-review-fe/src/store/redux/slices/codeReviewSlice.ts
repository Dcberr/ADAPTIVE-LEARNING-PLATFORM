import { createSlice, type PayloadAction } from "@reduxjs/toolkit"

type ReviewItem = {
  line: number
  message: string
  suggestion?: string
  type: "error" | "warning"
}

export type CodeReviewState = {
  code: string
  review: {
    errors: ReviewItem[]
    warnings: ReviewItem[]
    improvements: string[]
    understanding: string
  } | null
}

const initialState: CodeReviewState = {
  code: `int len = strlen(str);
  int j = 0;
  bool inSpace = false;
  int i = 0;

  while (i < len && str[i] == ' ') i++;

  for (; i < len; i++) {
      if (str[i] != ' ') {
          outstr[j++] = str[i];
          inSpace = false;
      } else {
          if (!inSpace) {
              outstr[j++] = ' ';
              inSpace = true;
          }
      }
  }

  if (j > 0 && outstr[j-1] == ' ') j--;

  outstr[j] = '\\0';`,
  review: null,
}

const codeReviewSlice = createSlice({
  name: "codeReview",
  initialState,
  reducers: {
    setCode: (state, action: PayloadAction<string>) => {
      state.code = action.payload
    },
    setReview: (state, action: PayloadAction<CodeReviewState["review"]>) => {
      state.review = action.payload
    },
  },
})

export const codeReviewReducer = codeReviewSlice.reducer
export const codeReviewActions = codeReviewSlice.actions
