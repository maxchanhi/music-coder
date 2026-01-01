import sys
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from interpreter import MusicCoderInterpreter


class MC2XML:
    def __init__(self, mc_file):
        with open(mc_file, 'r') as f:
            self.code = f.read()
        self.tokens = []
        
    def parse(self):
        interp = MusicCoderInterpreter(self.code)
        interp.tokenize()
        self.tokens = interp.tokens

    def generate_xml(self, output_file):
        score = ET.Element('score-partwise', version="3.1")
        
        # Part List
        part_list = ET.SubElement(score, 'part-list')
        score_part = ET.SubElement(part_list, 'score-part', id="P1")
        part_name = ET.SubElement(score_part, 'part-name')
        part_name.text = "MusicCoder Output"
        
        # Part
        part = ET.SubElement(score, 'part', id="P1")
        
        # Measure 1 (Attributes)
        measure_num = 1
        current_measure = ET.SubElement(part, 'measure', number=str(measure_num))
        
        attrs = ET.SubElement(current_measure, 'attributes')
        divs = ET.SubElement(attrs, 'divisions')
        divs.text = "1"
        key = ET.SubElement(attrs, 'key')
        fifths = ET.SubElement(key, 'fifths')
        fifths.text = "0"
        time = ET.SubElement(attrs, 'time')
        beats = ET.SubElement(time, 'beats')
        beats.text = "4"
        beat_type = ET.SubElement(time, 'beat-type')
        beat_type.text = "4"
        clef = ET.SubElement(attrs, 'clef')
        sign = ET.SubElement(clef, 'sign')
        sign.text = "G"
        line = ET.SubElement(clef, 'line')
        line.text = "2"
        
        current_beats = 0
        
        for token in self.tokens:
            ctype = token['type']
            
            # Check for Measure Full (Simple 4/4 logic)
            if current_beats >= 4:
                #measure_num += 1
                current_measure = ET.SubElement(part, 'measure', number=str(measure_num))
                current_beats = 0
            
            if ctype == 'LOOP_START':
                # If mid-measure, start new measure to ensure repeat sign is at start
                if current_beats > 0:
                    measure_num += 1
                    current_measure = ET.SubElement(part, 'measure', number=str(measure_num))
                    current_beats = 0

                # Barline Repeat Start
                barline = ET.SubElement(current_measure, 'barline', location="left")
                bar_style = ET.SubElement(barline, 'bar-style')
                bar_style.text = "heavy-light"
                repeat = ET.SubElement(barline, 'repeat', direction="forward")
                
            elif ctype == 'LOOP_END':
                # Barline Repeat End
                barline = ET.SubElement(current_measure, 'barline', location="right")
                bar_style = ET.SubElement(barline, 'bar-style')
                bar_style.text = "light-heavy"
                repeat = ET.SubElement(barline, 'repeat', direction="backward")
                
                # Force new measure after repeat end
                #measure_num += 1
                current_measure = ET.SubElement(part, 'measure', number=str(measure_num))
                current_beats = 0
                
            elif ctype == 'REST_H' or ctype == 'REST_Q':
                note_elem = ET.SubElement(current_measure, 'note')
                rest_elem = ET.SubElement(note_elem, 'rest')
                dur_elem = ET.SubElement(note_elem, 'duration')
                type_elem = ET.SubElement(note_elem, 'type')
                
                if ctype == 'REST_H':
                    dur_elem.text = "2"
                    type_elem.text = "half"
                    current_beats += 2
                else:
                    dur_elem.text = "1"
                    type_elem.text = "quarter"
                    current_beats += 1
                    
            elif ctype == 'NOTE':
                note_elem = ET.SubElement(current_measure, 'note')
                pitch = ET.SubElement(note_elem, 'pitch')
                

                midi_val = token['value']
                
                # C-1 = 0 (Standard MIDI)
                octave = (midi_val // 12) - 1
                step_val = midi_val % 12
                
                # Map step_val to Name + Alter
                # 0=C, 1=C#, 2=D, 3=D#, 4=E, 5=F, 6=F#, 7=G, 8=G#, 9=A, 10=A#, 11=B
                step_map = {
                    0: ('C', 0), 1: ('C', 1), 2: ('D', 0), 3: ('D', 1),
                    4: ('E', 0), 5: ('F', 0), 6: ('F', 1), 7: ('G', 0),
                    8: ('G', 1), 9: ('A', 0), 10: ('A', 1), 11: ('B', 0)
                }
                
                step_name, alter_val = step_map[step_val]
                
                step_elem = ET.SubElement(pitch, 'step')
                step_elem.text = step_name
                if alter_val != 0:
                    alter_elem = ET.SubElement(pitch, 'alter')
                    alter_elem.text = str(alter_val)
                octave_elem = ET.SubElement(pitch, 'octave')
                octave_elem.text = str(octave)
                
                dur_elem = ET.SubElement(note_elem, 'duration')
                dur_elem.text = "1" # Assume Quarter notes for all notes
                type_elem = ET.SubElement(note_elem, 'type')
                type_elem.text = "quarter"
                current_beats += 1
                
                # Articulations
                if token['staccato']:
                    notations = ET.SubElement(note_elem, 'notations')
                    artic = ET.SubElement(notations, 'articulations')
                    ET.SubElement(artic, 'staccato')
                    
        # Write to file
        xml_str = minidom.parseString(ET.tostring(score)).toprettyxml(indent="  ")
        with open(output_file, 'w') as f:
            f.write(xml_str)
        print(f"Successfully wrote {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mc2xml.py <mc_file> [output_xml]")
        sys.exit(1)
        
    mc_file = sys.argv[1]
    if len(sys.argv) >= 3:
        out_file = sys.argv[2]
    else:
        out_file = mc_file.rsplit('.', 1)[0] + ".musicxml"
        
    converter = MC2XML(mc_file)
    converter.parse()
    converter.generate_xml(out_file)
