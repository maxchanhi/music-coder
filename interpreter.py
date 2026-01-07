import sys
import re

class MusicCoderInterpreter:
    def __init__(self, source_code, debug=False):
        self.source_code = source_code
        self.tape = [0] * 30000
        self.ptr = 0
        self.debug = debug
        
        # Note values (MIDI numbers, C-1=0 C4=60))
        self.note_map = {}
        pitch_classes = {
            'C': 0, 'C#': 1, 'DB': 1,
            'D': 2, 'D#': 3, 'EB': 3,
            'E': 4,
            'F': 5, 'F#': 6, 'GB': 6,
            'G': 7, 'G#': 8, 'AB': 8,
            'A': 9, 'A#': 10, 'BB': 10,
            'B': 11
        }
        
        for name, base_val in pitch_classes.items():
            for octave in range(-1, 11): # -1 to 10
                midi_val = base_val + octave * 12 + 12 # Standard MIDI (C-1=0, C0=12, C4=60)
                if 0 <= midi_val <= 127:
                    self.note_map[f"{name}{octave}"] = midi_val
        
        self.tokens = []
        self.loop_map = {}
        self.loop_info = {} # Stores metadata for loops (e.g., fixed counts)

    def tokenize(self):
        # Remove comments <!-- ... -->
        clean_code = re.sub(r'<!--[^>]*>', '', self.source_code, flags=re.DOTALL)

        # Regex explanation:
        # \|:       -> Start Loop
        # :\|(?:x\d+|R4)? -> End Loop (optional xN or R4)
        # R4        -> Quarter Rest (Right)
        # R2        -> Half Rest (Left)
        # \|        -> Bar Line (Cosmetic)
        # [A-G][#b]?[0-9]?[._]* -> Note (optional sharp/flat) (optional octave) (suffixes: . _)
        
        # Updated regex to allow whitespace in loop suffix
        pattern = r'\|:|:\|(?:\s*(?:x\d+|R4))?|R4|R2|\||[A-G](?:#|b)?-?\d?(?:[._]+)?'
        raw_tokens = re.findall(pattern, clean_code, re.IGNORECASE)
        
        parsed_tokens = []
        for t in raw_tokens:
            t_upper = t.upper()
            if t_upper == '|:':
                parsed_tokens.append({'type': 'LOOP_START'})
            elif t_upper.startswith(':|'):
                # Check for xN or R4
                count = 'BF' # Default to Brainfuck mode
                is_infinite = False
                use_next_cell = False
                
                if 'R4' in t_upper:
                    use_next_cell = True
                    count = None # Determined at runtime
                elif 'X' in t_upper:
                    parts = t_upper.split('X')
                    if len(parts) == 2:
                        val_str = parts[1]
                        if val_str == '00':
                            is_infinite = True
                            count = None
                        else:
                            try:
                                count = int(val_str)
                            except ValueError:
                                pass 
                
                parsed_tokens.append({
                    'type': 'LOOP_END',
                    'count': count,
                    'infinite': is_infinite,
                    'use_next_cell': use_next_cell
                })
            elif t_upper == 'R4':
                parsed_tokens.append({'type': 'REST_Q'}) # Right
            elif t_upper == 'R2':
                parsed_tokens.append({'type': 'REST_H'}) # Left
            elif t_upper == '|':
                pass # Ignore bars completely
            else:

                # Match Note + Optional Octave + Optional Suffixes
                match = re.match(r'([A-G](?:#|B)?)(-?\d?)(.*)', t_upper)
                if match:
                    note_name = match.group(1)
                    octave_str = match.group(2)
                    suffixes = match.group(3)
                    
                    # Default Octave is 4 if not specified
                    octave = octave_str if octave_str else "4"
                    lookup_key = f"{note_name}{octave}"
                    
                    val = self.note_map.get(lookup_key)
                    
                    if val is None:
                         raise ValueError(f"Invalid or out-of-range note: {t_upper}")

                    parsed_tokens.append({
                        'type': 'NOTE',
                        'value': val,
                        'name': note_name,
                        'octave': octave,
                        'staccato': '.' in suffixes,
                        'legato': '_' in suffixes
                    })
        
        self.tokens = parsed_tokens
        self.build_loop_map()

    def build_loop_map(self):
        stack = []
        for i, token in enumerate(self.tokens):
            if token['type'] == 'LOOP_START':
                stack.append(i)
            elif token['type'] == 'LOOP_END':
                if not stack:
                    raise SyntaxError("Unmatched :| at token {}".format(i))
                start_index = stack.pop()
                self.loop_map[start_index] = i
                self.loop_map[i] = start_index
                
                # Register Loop Info
                self.loop_info[start_index] = {
                    'count': token['count'],
                    'infinite': token['infinite'],
                    'use_next_cell': token.get('use_next_cell', False)
                }
        if stack:
            raise SyntaxError("Unmatched |: at token {}".format(stack[0]))

    def run(self):
        self.tokenize()
        
        pc = 0
        prev_val = 0 # Track previous note value for interval arithmetic (0 = C-1)
        
        # Loop counters for fixed loops: { loop_start_pc: remaining_iterations }
        active_loops = {}

        if self.debug:
            print("DEBUG: Starting execution")
            print(f"DEBUG: Tape size: {len(self.tape)}")

        while pc < len(self.tokens):
            token = self.tokens[pc]
            ctype = token['type']
            
            if self.debug:
                print(f"DEBUG: PC={pc}, Token={ctype}, Ptr={self.ptr}, Val={self.tape[self.ptr]}, PrevNote={prev_val}")

            if ctype == 'REST_H': # R2 -> Left
                self.ptr -= 1
                prev_val = 0 # Reset previous note
                if self.ptr < 0:
                     # Pointer can't go left of 0
                     pass 
                
                if self.ptr < 0:
                     raise RuntimeError("Pointer moved left of 0")
            
            elif ctype == 'REST_Q': # R4 -> Right
                self.ptr += 1
                prev_val = 0 # Reset previous note
                if self.ptr >= len(self.tape):
                    self.tape.append(0)


            elif ctype == 'LOOP_START':
                info = self.loop_info.get(pc)
                
                if info['count'] == 'BF':
                    if self.tape[self.ptr] == 0:
                        pc = self.loop_map[pc]

                # Logic is now purely count-based (or infinite)
                # If infinite, count is None, infinite is True
                # If fixed, count is N, infinite is False

                elif pc not in active_loops:
                    if info['infinite']:
                        active_loops[pc] = -1 # Special marker for infinite
                    elif info['use_next_cell']:
                        end_pc = self.loop_map[pc]
                        lookahead_pc = end_pc + 1
                        note_count_val = 0
                        local_prev = 0
                        has_note_count = False
                        
                        while lookahead_pc < len(self.tokens) and self.tokens[lookahead_pc]['type'] == 'NOTE':
                            # Stop if note has suffixes (likely an instruction)
                            if self.tokens[lookahead_pc]['staccato'] or self.tokens[lookahead_pc]['legato']:
                                break
                            
                            has_note_count = True
                            curr_val = self.tokens[lookahead_pc]['value']
                            if curr_val > local_prev:
                                note_count_val += curr_val
                            elif curr_val < local_prev:
                                note_count_val -= curr_val
                            local_prev = curr_val
                            lookahead_pc += 1
                        
                        if has_note_count:
                            active_loops[pc] = note_count_val
                            # Store the skip count so we don't execute these notes later
                            self.loop_info[pc]['skip_count'] = lookahead_pc - (end_pc + 1)
                        else:
                            next_ptr = self.ptr + 1
                            if next_ptr < len(self.tape):
                                count_val = self.tape[next_ptr]
                            else:
                                count_val = 0 # Out of bounds default
                            active_loops[pc] = count_val
                    else:
                        active_loops[pc] = info['count']
                
            
            elif ctype == 'LOOP_END':
                start_pc = self.loop_map[pc]
                info = self.loop_info.get(start_pc)
                
                if info['count'] == 'BF':
                    if self.tape[self.ptr] != 0:
                        pc = start_pc
                else:
                    current_count = active_loops.get(start_pc)
                    
                    if current_count == -1:
                        # Infinite Loop
                        pc = start_pc
                    elif current_count is not None:
                        # Decrement remaining iterations
                        active_loops[start_pc] -= 1
                        if active_loops[start_pc] > 0:
                                pc = start_pc
                        else:
                                # Loop Finished
                                # Skip the notes that were used as count (if any)
                                skip_count = self.loop_info[start_pc].get('skip_count', 0)
                                pc += skip_count
                                del active_loops[start_pc]
            
            elif ctype == 'NOTE':
                current_val = token['value']
                
                # Arithmetic based on interval
                if current_val > prev_val:
                    # Ascending: Add Current Note
                    self.tape[self.ptr] = (self.tape[self.ptr] + current_val) % 256
                elif current_val < prev_val:
                    # Descending: Subtract Current Note
                    self.tape[self.ptr] = (self.tape[self.ptr] - current_val) % 256
                else:
                    # Equal: Look ahead to the NEXT note to determine operation
                    lookahead_pc = pc + 1
                    if lookahead_pc < len(self.tokens) and self.tokens[lookahead_pc]['type'] == 'NOTE':
                        next_val = self.tokens[lookahead_pc]['value']
                        diff = next_val - current_val
                        self.tape[self.ptr] = (self.tape[self.ptr] + diff) % 256
                        
                        # We must SKIP the next note because we just used it for "Brainfuck Arithmetic"
                        # If we don't skip, the next iteration will see Prev=Current, Next=Next, and perform standard Asc/Desc
                        # which adds large values.
                        
                        # Handle I/O flags of the CONSUMED note (since we skip its iteration)
                        consumed_token = self.tokens[lookahead_pc]
                        if consumed_token['staccato']:
                             sys.stdout.write(chr(self.tape[self.ptr]))
                        if consumed_token['legato']:
                             try:
                                 char = sys.stdin.read(1)
                                 if char:
                                     self.tape[self.ptr] = ord(char)
                                 else:
                                     self.tape[self.ptr] = 0
                             except:
                                 self.tape[self.ptr] = 0

                        pc += 1 # Advance PC to skip the next note
                        
                        # Update prev_val to the NOTE WE JUST CONSUMED
                        # This ensures continuity for the note AFTER the consumed one.
                        # Example: C4 -> C4 -> C#4 -> D4
                        # 1. C4 (+60). prev=60.
                        # 2. C4 (==). Lookahead C#4. Add +1. Tape=61. Skip C#4.
                        #    We need prev to be C#4 (61) so that D4 (62) is processed as 62>61?
                        #    Or should prev remain C4 (60)?
                        #    If this is just "+", we transitioned from C4 to C#4 state.
                        
                        current_val = next_val # Update current_val so prev_val gets updated correctly below
                    
                # Update previous value
                prev_val = current_val
                
                if token['staccato']:
                    sys.stdout.write(chr(self.tape[self.ptr]))
                if token['legato']:
                    try:
                        char = sys.stdin.read(1)
                        if char:
                            self.tape[self.ptr] = ord(char)
                        else:
                            self.tape[self.ptr] = 0
                    except:
                        self.tape[self.ptr] = 0

            pc += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <source_file> [--debug]")
        sys.exit(1)
        
    source_file = sys.argv[1]
    debug_mode = "--debug" in sys.argv

    with open(source_file, 'r') as f:
        code = f.read()
    
    interpreter = MusicCoderInterpreter(code, debug=debug_mode)
    interpreter.run()
