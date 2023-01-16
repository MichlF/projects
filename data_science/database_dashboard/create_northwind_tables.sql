/* 
 We first create separate tables within the northwind db
 Then, we load in our data from the .csv files.
 */
/* Create table categories */
CREATE TABLE categories (
    categoryID INT PRIMARY KEY NOT NULL,
    categoryName VARCHAR(100) NOT NULL,
    description VARCHAR(255) DEFAULT 'no description provided',
    picture TEXT
);

/* Create table customers */
CREATE TABLE customers (
    customerID VARCHAR(100) PRIMARY KEY NOT NULL,
    companyName VARCHAR(100) NOT NULL,
    contactName VARCHAR(100),
    contactTitle VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(100),
    region VARCHAR(100),
    postalCode VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(100),
    fax VARCHAR(100)
);

/* Create table regions */
CREATE TABLE regions (
    regionID INT PRIMARY KEY NOT NULL,
    regionDescription VARCHAR(255)
);

/* Create table shippers */
CREATE TABLE shippers (
    shipperID INT PRIMARY KEY NOT NULL,
    companyName VARCHAR(255) NOT NULL,
    phone VARCHAR(100)
);

/* Create table suppliers */
CREATE TABLE suppliers (
    supplierID INT PRIMARY KEY NOT NULL,
    companyName VARCHAR(255),
    contactName VARCHAR(100),
    contactTitle VARCHAR(100),
    address VARCHAR(100),
    city VARCHAR(100),
    region VARCHAR(100),
    postalCode VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(100),
    fax VARCHAR(100),
    homePage VARCHAR(255)
);

/* Create employees */
CREATE TABLE employees (
    employeeID INT PRIMARY KEY NOT NULL,
    lastName VARCHAR(100) NOT NULL,
    firstName VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    titleOfCourtesy VARCHAR(100),
    birthDate DATE,
    hireDate DATE,
    address VARCHAR(255),
    city VARCHAR(100),
    region VARCHAR(100),
    postalCode VARCHAR(100),
    country VARCHAR(100),
    homePhone VARCHAR(100),
    extension INT,
    photo TEXT,
    notes TEXT,
    reportsTo INT,
    photoPath TEXT,
    FOREIGN KEY (reportsTo) REFERENCES employees(employeeID)
);

/* Create table products */
CREATE TABLE products (
    productID INT PRIMARY KEY NOT NULL,
    productName VARCHAR(100),
    supplierID INT,
    categoryID INT,
    quantityPerUnit VARCHAR(100),
    unitPrice FLOAT,
    unitsInStock INT,
    unitsOnOrder INT,
    reorderLevel INT,
    discontinued INT,
    FOREIGN KEY (supplierID) REFERENCES suppliers(supplierID),
    FOREIGN KEY (categoryID) REFERENCES categories(categoryID)
);

/* Create table orders */
CREATE TABLE orders (
    orderID INT PRIMARY KEY NOT NULL,
    customerID VARCHAR(50),
    employeeID INT,
    orderDate DATE,
    requiredDate DATE,
    shippedDate DATE,
    shipVia INT,
    freight FLOAT,
    shipName VARCHAR(100),
    shipAddress VARCHAR(255),
    shipCity VARCHAR(100),
    shipRegion VARCHAR(100),
    shipPostalCode VARCHAR(100),
    shipCountry VARCHAR(100),
    FOREIGN KEY (customerID) REFERENCES customers(customerID),
    FOREIGN KEY (employeeID) REFERENCES employees(employeeID),
    FOREIGN KEY (shipVia) REFERENCES shippers(shipperID)
);

/* Create table order_details */
CREATE TABLE order_details (
    orderID INT NOT NULL,
    productID INT NOT NULL,
    unitPrice FLOAT,
    quantity INT,
    discount FLOAT,
    FOREIGN KEY (productID) REFERENCES products(productID),
    FOREIGN KEY (orderID) REFERENCES orders(orderID)
);

/* Create table territories */
CREATE TABLE territories (
    territoryID INT PRIMARY KEY NOT NULL,
    territoryDescription VARCHAR(100),
    regionID INT,
    FOREIGN KEY (regionID) REFERENCES regions(regionID)
);

/* Create table employee_territories */
CREATE TABLE employee_territories (
    employeeID INT NOT NULL,
    territoryID INT NOT NULL REFERENCES territories(territoryID),
    FOREIGN KEY (employeeID) REFERENCES employees(employeeID)
);

/* 
Create country code table (not part of the Northwind DB)
find the list here: https://gist.github.com/vvaezian/8c03a6773df51b0f966c3c7f50c4c35f 
*/
CREATE TABLE country_codes (
    country VARCHAR(100),
    countrycode VARCHAR(2)
);

/* 
 Now that we've created all tables, we copy the contents in each of these tables from our .csv files.
 The local folder path is: C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\
 Note: We need to use the \COPY command instead of the COPY command because we are executing from psql's internal environment
 Note: You definitely want to explicitly control ENCODING otherwise you may in for trouble figuring out why special characters are all f up...
 */
\COPY categories FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\categories.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY customers FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\customers.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY regions FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\regions.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY shippers FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\shippers.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY suppliers FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\suppliers.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY employees FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\employees.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY products FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\products.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY orders FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\orders.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY order_details FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\order_details.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY territories FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\territories.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY employee_territories FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\employee_territories.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';

\COPY country_codes FROM 'C:\Users\miche\Documents\GitHub\spiced_projects\week_05\northwind\country_codes.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL' ENCODING 'UTF8';