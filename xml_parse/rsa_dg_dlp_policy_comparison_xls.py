#!/usr/local/bin/python
from lxml import etree
import xlsxwriter
import ast

doc = etree.parse('policy_list_predefined.xml')
policy_list = {}

with open('rsa_dlp_policy.txt') as infile:
  #Read RSA policy definitions from file & convert to dictionary
  rsa_pol = ast.literal_eval((infile.read()))

#print "rsa_pol: ", rsa_pol

for elt in doc.getiterator('policy'):
  #print "========================="
  for i in range(len(elt)):
    if elt[i].tag == 'name':
      #print "Policy Name = ", elt[i].text
      pol_name = elt[i].text.strip()
      policy_list[pol_name] = []
    if elt[i].tag == 'policy_rule':
      for pol_elt in elt[i].getiterator('value'):
        #print pol_elt.text
        policy_list[pol_name].append(pol_elt.text.strip())
  policy_list[pol_name] = list(set(policy_list[pol_name]))

# Dictionary output:
#print "policy_list = ", policy_list

#Text output
#for key in policy_list:
#  print "%s\t: %s"%(key,policy_list[key])

workbook = xlsxwriter.Workbook('dg_dlp_1.xlsx')
try:
  bold = workbook.add_format({'bold': True})
  worksheet = workbook.add_worksheet()
  worksheet.set_column('A:C', 55)

  worksheet.write(0,0, 'POLICY', bold)
  worksheet.write(0,1, 'DG', bold)
  worksheet.write(0,2, 'RSA', bold)

  row = 1
  col = 0

  for key in policy_list.keys():
    row += 1
    dg_row = rsa_row = row
    worksheet.write(row, col, key)
    for item in policy_list[key]:
        worksheet.write(dg_row, col + 1, item)
        dg_row += 1

    if key in rsa_pol:
      for item in rsa_pol[key]:
        worksheet.write(rsa_row, col + 2, item)
        rsa_row += 1

    row = max(dg_row,rsa_row)

  for key in rsa_pol.keys():
    if key not in policy_list:
      row += 1
      worksheet.write(row, col, key)
      for item in rsa_pol[key]:
        worksheet.write(row, col + 2, item)
        row += 1

except Exception as ne:
  print "Exception: ", ne
finally:
  workbook.close()

