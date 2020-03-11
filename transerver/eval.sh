for i in {0..20}
do
  echo ${i}
  python translate.py --id ${i}
done
