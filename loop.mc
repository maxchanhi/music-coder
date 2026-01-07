D#-1        <!-- Set Loop Counter tape[0] to 3 >
R4 C5       <!-- Move to tape[1], Set 'H' (72) >
R2          <!-- Move back to tape[0] for loop condition >
|:          <!-- Start Loop (while tape[0] != 0) >
  R4 C-1.   <!-- Move to tape[1], Output 'H' >
  R2        <!-- Move back to tape[0] >
  E-1 D#-1 D-1 <!-- Decrement tape[0] by 1 using Equal arithmetic >
:|          <!-- End Loop >
