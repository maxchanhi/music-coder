import sys
import xml.etree.ElementTree as ET
from interpreter import MusicCoderInterpreter


class XML2MC:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.raw_tokens = []
        self.mc_tokens = []
        
    def parse(self):
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        
        # Traverse parts (assuming P1 for now or iterate all)
        for part in root.findall('part'):
            for measure in part.findall('measure'):
                # Check for barlines and notes in order
                for child in measure:
                    if child.tag == 'barline':
                        repeat = child.find('repeat')
                        if repeat is not None:
                            direction = repeat.get('direction')
                            if direction == 'start' or direction == 'forward':
                                self.raw_tokens.append({'type': 'BARLINE', 'value': '|:'})
                            elif direction == 'backward':
                                self.raw_tokens.append({'type': 'BARLINE', 'value': ':|'})
                    
                    elif child.tag == 'note':
                        # Check for Rest
                        rest = child.find('rest')
                        if rest is not None:
                            duration = child.find('duration')
                            dur_val = 1
                            if duration is not None:
                                dur_val = int(duration.text)
                            
                            token_str = 'R2' if dur_val >= 2 else 'R4'
                            self.raw_tokens.append({'type': 'REST', 'value': token_str})
                            continue
                        
                        # Pitch
                        pitch = child.find('pitch')
                        if pitch is not None:
                            step = pitch.find('step').text
                            alter_elem = pitch.find('alter')
                            alter = int(alter_elem.text) if alter_elem is not None else 0
                            octave_elem = pitch.find('octave')
                            octave = int(octave_elem.text) if octave_elem is not None else 4
                            
                            # Reconstruct Note Name
                            note_name = step
                            if alter == 1:
                                note_name += '#'
                            elif alter == -1:
                                note_name += 'B'
                                
                            # Articulations (Staccato)
                            staccato = False
                            notations = child.find('notations')
                            if notations is not None:
                                articulations = notations.find('articulations')
                                if articulations is not None:
                                    if articulations.find('staccato') is not None:
                                        staccato = True
                                        
                            self.raw_tokens.append({
                                'type': 'NOTE',
                                'name': note_name,
                                'octave': octave,
                                'staccato': staccato
                            })

    def resolve_tokens(self):
        for i, token in enumerate(self.raw_tokens):
            if token['type'] == 'BARLINE' or token['type'] == 'REST':
                self.mc_tokens.append(token['value'])
                continue
            
            if token['type'] == 'NOTE':
                note_str = token['name']
                octave = token['octave']
                
                # Append octave if not 4 (default)
                if octave != 4:
                    note_str += str(octave)
                
                if token['staccato']:
                    note_str += "."
                    
                self.mc_tokens.append(note_str)

    def get_code(self):
        return " ".join(self.mc_tokens)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xml2mc.py <xml_file>")
        sys.exit(1)
        
    xml_file = sys.argv[1]
    converter = XML2MC(xml_file)
    converter.parse()
    converter.resolve_tokens()
    code = converter.get_code()
    
    print("Recovered MC Code:")
    print(code)
    print("-" * 20)
    print("Executing Code:")
    
    interpreter = MusicCoderInterpreter(code)
    interpreter.run()
