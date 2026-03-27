@echo off
cd database/mysql
powershell "mysql -u root -p'root123' healthfit_db < schema.sql"
powershell "mysql -u root -p'root123' healthfit_db < sample_data.sql"
echo Loaded!
pause
