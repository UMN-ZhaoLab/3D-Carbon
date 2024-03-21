import sys
import yaml
import argparse
from api import print_carbon,exploration,AV,draw_AV,print_design
from models.die import die


'''
print("===> Example of AMD EPYC 7000 series using 2.5D MCM integration")
print_carbon('MCM/EPYC_7351P.yaml')
print_carbon('MCM/EPYC_7402.yaml')
print_carbon('MCM/EPYC_7272.yaml')
print_carbon('MCM/EPYC_7702.yaml')
print_carbon('MCM//EPYC_7513.yaml')
'''
def main():
    parser = argparse.ArgumentParser(description='print')
    parser.add_argument('a', type=str, help='yaml')
    args = parser.parse_args()

    print_design(args.a)

if __name__ == "__main__":
    main()