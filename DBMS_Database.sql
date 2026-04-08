CREATE DATABASE IF NOT EXISTS Dbms_Project;
USE Dbms_Project;


CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    DOB DATE,
    email_id VARCHAR(100) UNIQUE NOT NULL,
    phone_no VARCHAR(15)
);

DELIMITER $$

CREATE TRIGGER trg_users_check_dob_insert
BEFORE INSERT ON Users
FOR EACH ROW
BEGIN
    IF NEW.dob IS NOT NULL AND NEW.dob > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'DOB cannot be in the future';
    END IF;
END$$

CREATE TRIGGER trg_users_check_dob_update
BEFORE UPDATE ON Users
FOR EACH ROW
BEGIN
    IF NEW.dob IS NOT NULL AND NEW.dob > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'DOB cannot be in the future';
    END IF;
END$$

DELIMITER ;


CREATE TABLE Role (
    role_type VARCHAR(30) PRIMARY KEY,
    CHECK (role_type IN ('Admin', 'Organizer', 'Speaker', 'Attendee'))
);

CREATE TABLE User_Role (
    user_id INT,
    role_type VARCHAR(30),
    PRIMARY KEY (user_id, role_type),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (role_type) REFERENCES Role(role_type)
);


CREATE TABLE Venue (
    venue_id INT AUTO_INCREMENT PRIMARY KEY,
    venue_name VARCHAR(100) NOT NULL,
    max_capacity INT NOT NULL,
    venue_status VARCHAR(30),
    street VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    CHECK (max_capacity > 0),
    CHECK (venue_status IN ('Available', 'Unavailable', 'Under-Maintenance')),
    UNIQUE (street, city, state, pincode)
);


CREATE TABLE Event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    registration_fees DECIMAL(10,2),
    registration_deadline DATE,
    event_status ENUM('Draft', 'Upcoming', 'Ongoing', 'Completed', 'Cancelled'),
    description TEXT,
    total_registrations INT DEFAULT 0,
    available_slots INT DEFAULT 0,
    venue_id INT,
    FOREIGN KEY (venue_id) REFERENCES Venue(venue_id),
    CHECK (end_date >= start_date),
    CHECK (registration_fees >= 0)
);


CREATE TABLE Event_Registration (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    event_id INT,
    registration_date DATE NOT NULL,
    registration_status ENUM('Confirmed', 'Cancelled', 'Pending'),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
);


CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    registration_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_mode ENUM('UPI', 'Card', 'NetBanking', 'Cash') NOT NULL,
    payment_status ENUM('Success', 'Failed', 'Pending') NOT NULL,
    payment_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (registration_id) REFERENCES Event_Registration(registration_id),
    CHECK (amount >= 0)
);

DELIMITER $$

CREATE TRIGGER trg_payment_success_confirm_registration
AFTER INSERT ON Payment
FOR EACH ROW
BEGIN
    IF NEW.payment_status = 'Success' THEN
        UPDATE Event_Registration
        SET registration_status = 'Confirmed'
        WHERE registration_id = NEW.registration_id;
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_event_registration_count
AFTER INSERT ON Event_Registration
FOR EACH ROW
BEGIN
    IF NEW.registration_status = 'Confirmed' THEN
        UPDATE Event
        SET total_registrations = total_registrations + 1,
            available_slots = available_slots - 1
        WHERE event_id = NEW.event_id;
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_prevent_event_overbooking
BEFORE INSERT ON Event_Registration
FOR EACH ROW
BEGIN
    DECLARE slots_left INT;

    SELECT available_slots
    INTO slots_left
    FROM Event
    WHERE event_id = NEW.event_id;

    IF slots_left <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Event is fully booked';
    END IF;
END$$

DELIMITER ;


CREATE TABLE Session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    speaker_user_id INT,
    title VARCHAR(100) NOT NULL,
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    total_slots INT NOT NULL,
    slots_filled INT DEFAULT 0,
    FOREIGN KEY (event_id) REFERENCES Event(event_id),
    FOREIGN KEY (speaker_user_id) REFERENCES Users(user_id),
    CHECK (end_time > start_time),
    CHECK (slots_filled <= total_slots)
);

CREATE TABLE Session_Registration (
    session_registration_no INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    session_id INT,
    session_registration_date DATE,
    session_registration_status VARCHAR(30),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (session_id) REFERENCES Session(session_id),
    CHECK (session_registration_status IN ('Registered', 'Cancelled'))
);

DELIMITER $$

CREATE TRIGGER trg_prevent_session_overbooking
BEFORE INSERT ON Session_Registration
FOR EACH ROW
BEGIN
    DECLARE filled INT;
    DECLARE capacity INT;

    SELECT slots_filled, total_slots
    INTO filled, capacity
    FROM Session
    WHERE session_id = NEW.session_id;

    IF filled >= capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Session is fully booked';
    END IF;
END$$

CREATE TRIGGER trg_update_session_slots
AFTER INSERT ON Session_Registration
FOR EACH ROW
BEGIN
    UPDATE Session
    SET slots_filled = slots_filled + 1
    WHERE session_id = NEW.session_id;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_cancel_event_registrations
AFTER UPDATE ON Event
FOR EACH ROW
BEGIN
    IF OLD.event_status <> 'Cancelled'
       AND NEW.event_status = 'Cancelled' THEN

        UPDATE Event_Registration
        SET registration_status = 'Cancelled'
        WHERE event_id = NEW.event_id;

        UPDATE Session_Registration sr
        JOIN Session s ON sr.session_id = s.session_id
        SET sr.session_registration_status = 'Cancelled'
        WHERE s.event_id = NEW.event_id;
    END IF;
END$$

DELIMITER ;


CREATE TABLE Resource (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_name VARCHAR(100) NOT NULL,
    resource_type ENUM('Furniture', 'Merchandise', 'Refreshments','Session_Requirement') NOT NULL,
    total_quantity INT NOT NULL,
    available_quantity INT NOT NULL,
    status ENUM('Available', 'Allocated', 'Unavailable') NOT NULL,
    storage_location VARCHAR(100),
    CHECK (total_quantity > 0),
    CHECK (available_quantity >= 0),
    CHECK (available_quantity <= total_quantity)
);

CREATE TABLE Resource_Allocation (
    session_id INT,
    resource_id INT,
    quantity_allocated INT NOT NULL,
    allocation_status ENUM('Allocated', 'Released') NOT NULL,
    start_time TIME,
    end_time TIME,
    usage_completed BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (session_id, resource_id),
    FOREIGN KEY (session_id) REFERENCES Session(session_id),
    FOREIGN KEY (resource_id) REFERENCES Resource(resource_id),
    CHECK (quantity_allocated > 0),
    CHECK (end_time > start_time)
);

DELIMITER $$

CREATE TRIGGER trg_check_resource_availability
BEFORE INSERT ON Resource_Allocation
FOR EACH ROW
BEGIN
    DECLARE available INT;
    DECLARE r_status VARCHAR(30);

    SELECT available_quantity, status
    INTO available, r_status
    FROM Resource
    WHERE resource_id = NEW.resource_id;

    IF r_status <> 'Available' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Resource is not available for allocation';
    END IF;

    IF NEW.quantity_allocated > available THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient resource quantity';
    END IF;
END$$

CREATE TRIGGER trg_update_resource_quantity
AFTER INSERT ON Resource_Allocation
FOR EACH ROW
BEGIN
    UPDATE Resource
    SET available_quantity = available_quantity - NEW.quantity_allocated
    WHERE resource_id = NEW.resource_id;
END$$

CREATE TRIGGER trg_handle_resource_release
AFTER UPDATE ON Resource_Allocation
FOR EACH ROW
BEGIN
    DECLARE r_type VARCHAR(50);

    IF NEW.usage_completed = TRUE
       AND OLD.usage_completed = FALSE THEN

        SELECT resource_type
        INTO r_type
        FROM Resource
        WHERE resource_id = NEW.resource_id;

        IF r_type = 'Furniture' THEN
            UPDATE Resource
            SET available_quantity = available_quantity + NEW.quantity_allocated
            WHERE resource_id = NEW.resource_id;
        END IF;

        UPDATE Resource_Allocation
        SET allocation_status = 'Released'
        WHERE session_id = NEW.session_id
          AND resource_id = NEW.resource_id;
    END IF;
END$$

DELIMITER ;


CREATE INDEX idx_event_registration_event
ON Event_Registration(event_id);

CREATE INDEX idx_event_registration_status
ON Event_Registration(registration_status);

CREATE INDEX idx_payment_registration
ON Payment(registration_id);

CREATE INDEX idx_payment_status
ON Payment(payment_status);

CREATE INDEX idx_session_event
ON Session(event_id);

CREATE INDEX idx_session_speaker
ON Session(speaker_user_id);

CREATE INDEX idx_session_registration_session
ON Session_Registration(session_id);

CREATE INDEX idx_session_registration_user
ON Session_Registration(user_id);

CREATE INDEX idx_resource_allocation_resource
ON Resource_Allocation(resource_id);

CREATE INDEX idx_event_status
ON Event(event_status);

CREATE INDEX idx_event_dates
ON Event(start_date, end_date);

ALTER TABLE Venue
ADD COLUMN venue_room VARCHAR(50) NOT NULL AFTER venue_name;
SHOW CREATE TABLE Venue;

ALTER TABLE Venue
DROP INDEX street;

ALTER TABLE Venue
ADD CONSTRAINT uq_venue_location
UNIQUE (venue_name, street, city, state, pincode);

CREATE TABLE Vendor (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL,
    vendor_type ENUM('Stationery','Music','Food','Decoration','Technical','Other') NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    phone_no VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    street VARCHAR(100),
    city ENUM('Delhi','Bangalore','Mumbai','Pune','Chennai','Kolkata','Jaipur','Hyderabad','Ahmedabad') NOT NULL,
    state VARCHAR(50),
    pincode VARCHAR(10) NOT NULL,
    courier_facility BOOLEAN NOT NULL DEFAULT FALSE,

    CHECK (phone_no REGEXP '^[0-9]{10}$'),
    CHECK (pincode REGEXP '^[0-9]{6}$')
);

CREATE TABLE Vendor_Material (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT,
    material_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50),   -- per piece, per kg, per box etc
    FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id),
    CHECK (price >= 0)
);

ALTER TABLE Venue
MODIFY city ENUM('Delhi','Bangalore','Mumbai','Pune','Chennai','Kolkata','Jaipur','Hyderabad','Ahmedabad') NOT NULL;

ALTER TABLE Venue
DROP INDEX uq_venue_location;

ALTER TABLE Venue
ADD CONSTRAINT uq_venue_location
UNIQUE (venue_name, street, city, pincode);

ALTER TABLE Role
DROP CHECK role_chk_1;

ALTER TABLE Role
DROP PRIMARY KEY;

SHOW CREATE TABLE User_Role;

ALTER TABLE User_Role
DROP FOREIGN KEY user_role_ibfk_1;

ALTER TABLE Role
DROP PRIMARY KEY;

SELECT TABLE_NAME, CONSTRAINT_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_NAME = 'Role';

ALTER TABLE User_Role
DROP FOREIGN KEY user_role_ibfk_2;

ALTER TABLE Role
DROP PRIMARY KEY;

DROP TABLE Role;

CREATE TABLE Role (
    role_type ENUM('Admin','Organizer','Speaker','Attendee','Performer') PRIMARY KEY NOT NULL
);

Select * from User_Role;

ALTER TABLE User_Role
ADD FOREIGN KEY (role_type) REFERENCES Role(role_type);

ALTER TABLE User_Role
MODIFY role_type ENUM('Admin','Organizer','Speaker','Attendee','Performer') NOT NULL;

ALTER TABLE Event_Registration
ADD COLUMN govt_id_type ENUM('Aadhar','Passport','Driving License','PAN') NOT NULL,
ADD COLUMN govt_id_number VARCHAR(50) NOT NULL UNIQUE;

ALTER TABLE Session_Registration
ADD COLUMN govt_id_type ENUM('Aadhar','Passport','Driving License','PAN') NOT NULL,
ADD COLUMN govt_id_number VARCHAR(50) NOT NULL UNIQUE;

ALTER TABLE Event
ADD CHECK (total_registrations >= 0),
ADD CHECK (available_slots >= 0);

ALTER TABLE Session
ADD CHECK (total_slots > 0),
ADD CHECK (slots_filled >= 0);

ALTER TABLE Resource_Allocation
ADD CHECK (quantity_allocated > 0);

ALTER TABLE Users
MODIFY phone_no VARCHAR(15) NOT NULL,
ADD CONSTRAINT chk_phone_numeric
CHECK (phone_no REGEXP '^[0-9]{10}$');

ALTER TABLE Users
ADD CONSTRAINT chk_first_name
CHECK (first_name REGEXP '^[A-Za-z]+$');

ALTER TABLE Users
ADD CONSTRAINT chk_last_name
CHECK (last_name REGEXP '^[A-Za-z]+$');

ALTER TABLE Venue
MODIFY venue_status ENUM('Available','Unavailable','Under-Maintenance') NOT NULL;

ALTER TABLE Event
MODIFY event_type ENUM(
'Keynote Talk',
'Performance',
'Panel Discussion',
'Workshop'
) NOT NULL;

ALTER TABLE Session_Registration
MODIFY session_registration_status 
ENUM('Registered','Cancelled') NOT NULL;

Show tables; 

INSERT INTO Users (first_name, last_name, dob, email_id, phone_no) VALUES
('Smridhi','Tandon','1998-04-12','smridhi@email.com','9876543210');

INSERT INTO Users (first_name, last_name, dob, email_id, phone_no) VALUES
('Monica','Geller','1995-08-21','Monica@email.com','9876501234'),
('Chandler','Bing','2000-01-10','Chandler@email.com','9876512345'),
('Rachel','Green','1992-07-15','Rachel@email.com','9876523456'),
('Harry','Potter','1999-09-30','Harry31@email.com','9876534567');

INSERT INTO Role VALUES
('Admin'),
('Organizer'),
('Speaker'),
('Attendee'),
('Performer');

INSERT INTO User_Role VALUES
(1,'Admin'),
(2,'Organizer'),
(3,'Speaker'),
(4,'Attendee'),
(5,'Performer'),
(3,'Attendee');

ALTER TABLE Venue
DROP CONSTRAINT uq_venue_location;

ALTER TABLE Venue
ADD CONSTRAINT uq_venue_location
UNIQUE (venue_room, venue_name, street, city, pincode);

INSERT INTO Venue (venue_name, venue_room, max_capacity, venue_status, street, city, pincode)VALUES
('JLN Stadium','Hall A',300,'Available','JLN Road','Delhi','110076'),
('Grand Arena','Auditorium 1',200,'Available','MG Road','Mumbai','400001'),
('JLN Stadium','Hall C',250,'Available','JLN Road','Delhi','110076'),
('XYZ Mall','Audi 102',50,'Unavailable','Mysore Road','Bangalore','560032');

Select * from Venue;

INSERT INTO Event (event_name,event_type,start_date,end_date,registration_fees, registration_deadline,event_status,
					description, total_registrations,available_slots,venue_id) VALUES
('AI Innovation Summit','Keynote Talk','2026-05-10','2026-05-12', 2000,'2026-05-01','Upcoming', 'AI and ML conference',0 ,300, 5),
('Music Fiesta','Performance','2026-06-15','2026-06-15', 1000,'2026-06-10','Upcoming', 'Live music performances',0,200, 6),
('Book Launch','Keynote Talk','2026-05-10','2026-05-12', 2000,'2026-05-10','Upcoming', 'Book Launch - Percy Jackson: The Adventures Continue, by Rick Riordon',0 ,300, 5);


DELIMITER $$

CREATE TRIGGER trg_prevent_event_overlap
BEFORE INSERT ON Event
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Event e
        WHERE e.venue_id = NEW.venue_id
        AND NOT (
            NEW.end_date < e.start_date
            OR
            NEW.start_date > e.end_date
        )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Event dates overlap at this venue';
    END IF;
END$$

DELIMITER ;

Delete from Event Where venue_id = 5;

Select * from Event;

SHOW TRIGGERS LIKE 'Event';

INSERT INTO Event (event_name,event_type,start_date,end_date,registration_fees, registration_deadline,event_status,
					description, total_registrations,available_slots,venue_id) VALUES
('AI Innovation Summit','Keynote Talk','2026-05-10','2026-05-12', 2000,'2026-05-01','Upcoming', 'AI and ML conference',0 ,300, 5),
('Book Launch','Keynote Talk','2026-05-10','2026-05-12', 2000,'2026-05-10','Upcoming', 'Book Launch - Percy Jackson: The Adventures Continue, by Rick Riordon',0 ,300, 5);
-- The above input should give error since same venue has two events on same dates

INSERT INTO Event(event_name,event_type,start_date,end_date,registration_fees, registration_deadline,event_status,
					description, total_registrations,available_slots,venue_id) VALUES
('AI Innovation Summit','Keynote Talk','2026-05-10','2026-05-12', 2000,'2026-05-01','Upcoming', 'AI and ML conference',0 ,300, 5),
('Book Launch','Keynote Talk','2026-05-13','2026-05-13', 2000,'2026-05-10','Upcoming', 'Book Launch - Percy Jackson: The Adventures Continue, by Rick Riordon',0 ,300, 5);

DELIMITER $$

CREATE TRIGGER trg_prevent_session_overlap
BEFORE INSERT ON Session
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Session s
        WHERE s.event_id = NEW.event_id
        AND s.session_date = NEW.session_date
        AND NOT (
            NEW.end_time <= s.start_time
            OR
            NEW.start_time >= s.end_time
        )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Session time overlaps within this event';
    END IF;
END$$

DELIMITER ;

INSERT INTO Session(event_id,speaker_user_id,title,session_date,start_time,end_time,total_slots) VALUES
(18,3,'Future of AI','2026-05-10','10:00:00','11:30:00',100),
(18,3,'AI in medicine','2026-05-10','10:00:00','11:30:00',100),
(8,5,'Live Band Performance','2026-06-15','18:00:00','20:00:00',150);

delete from Session where event_id = 18;

INSERT INTO Session(event_id,speaker_user_id,title,session_date,start_time,end_time,total_slots) VALUES
(18,3,'Future of AI','2026-05-10','10:00:00','11:30:00',100),
(18,3,'AI in medicine','2026-05-10','11:30:00','12:30:00',100);

INSERT INTO Event_Registration (user_id,event_id,registration_date,registration_status,govt_id_type,govt_id_number) VALUES
(4,18,CURDATE(),'Confirmed','Aadhar','123456789012'),
(5,8,CURDATE(),'Confirmed','Passport','P1234567');

select * from Event_Registration;

INSERT INTO Payment (registration_id,amount,payment_mode,payment_status) VALUES
(5,2000,'UPI','Success'),
(6,1000,'Card','Success');

select * from Session;

ALTER TABLE Session_Registration
DROP INDEX govt_id_number;

ALTER TABLE Session_Registration
ADD CONSTRAINT uq_session_govtid
UNIQUE (session_id, govt_id_number);

DELIMITER $$

CREATE TRIGGER trg_validate_session_registration
BEFORE INSERT ON Session_Registration
FOR EACH ROW
BEGIN
    DECLARE event_exists INT;

    SELECT COUNT(*)
    INTO event_exists
    FROM Event_Registration er
    JOIN Session s ON er.event_id = s.event_id
    WHERE er.user_id = NEW.user_id
      AND s.session_id = NEW.session_id
      AND er.registration_status = 'Confirmed';

    IF event_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User must be registered for the event before registering for a session';
    END IF;
END$$

DELIMITER ;

delete from session_registration where session_id = 6;
select * from session;

INSERT INTO Session_Registration (user_id,session_id,session_registration_date, session_registration_status,govt_id_type,govt_id_number) VALUES
(4,11,CURDATE(),'Registered','Aadhar','123456789012'),
(4,12,CURDATE(),'Registered','Aadhar','123456789012'),
(5,6,CURDATE(),'Registered','Passport','P1234567');

INSERT INTO Vendor (vendor_name, vendor_type, contact_person, phone_no, email, street, city, state, pincode, courier_facility) VALUES
('Elite Stationers','Stationery','Suresh Agarwal','9123456780', 'elite@email.com','Karol Bagh','Delhi','Delhi','110005',TRUE),
('SoundWave Systems','Music','Rohan Malhotra','9234567890','soundwave@email.com','Indiranagar','Bangalore','Karnataka','560038',TRUE),
('DecorXpress','Decoration','Meena Patel','9345678901','decor@email.com','Navrangpura','Ahmedabad','Gujarat','380009',FALSE),
('Catering Kings','Food','Imran Sheikh','9456789012','catering@email.com','Bandra West','Mumbai','Maharashtra','400050',TRUE),
('StageCraft Solutions','Technical','Vikas Nair','9567890123','stagecraft@email.com','T Nagar','Chennai','Tamil Nadu','600017',FALSE),
('PrintHub','Stationery','Kunal Arora','9678901234','print@email.com','Hitech City','Hyderabad','Telangana','500081',TRUE);

INSERT INTO Vendor_Material (vendor_id, material_name, price, unit) VALUES
-- Elite Stationers
(1,'Notebook',40,'per piece'), (1,'Ball Pen',10,'per piece'), (1,'Conference Folder',120,'per piece'),

-- SoundWave Systems
(2,'PA System',15000,'per event'), (2,'Wireless Microphone',2000,'per unit'), (2,'DJ Console',25000,'per event'),

-- DecorXpress
(3,'Stage Backdrop',8000,'per setup'), (3,'Flower Decoration',5000,'per event'), (3,'LED Lighting',7000,'per setup'),

-- Catering Kings
(4,'Veg Buffet',450,'per plate'), (4,'Non-Veg Buffet',650,'per plate'), (4,'Snack Counter',150,'per person'),

-- StageCraft Solutions
(5,'LED Screen',20000,'per event'), (5,'Stage Platform',12000,'per setup'), (5,'Truss Structure',10000,'per setup'),

-- PrintHub
(6,'Event Banner',1500,'per piece'), (6,'ID Cards',25,'per piece'), (6,'Brochure Printing',15,'per copy');

INSERT INTO Resource (resource_name, resource_type, total_quantity, available_quantity, status, storage_location) VALUES
('Plastic Chairs','Furniture',500,500,'Available','Warehouse A'),
('Round Tables','Furniture',100,100,'Available','Warehouse A'),
('Projector','Session_Requirement',10,10,'Available','AV Room'),
('Wireless Microphone','Session_Requirement',20,20,'Available','AV Room'),
('LED Screen','Session_Requirement',5,5,'Available','AV Room'),
('Event T-Shirts','Merchandise',1000,1000,'Available','Store Room'),
('Welcome Kits','Merchandise',500,500,'Available','Store Room'),
('Lunch Meal Boxes','Refreshments',800,800,'Available','Catering Area'),
('Snack Packs','Refreshments',600,600,'Available','Catering Area');

select * from session;

INSERT INTO Resource_Allocation (session_id, resource_id, quantity_allocated, allocation_status, start_time, end_time) VALUES
-- AI Session (Session 11)
(11,1,150,'Allocated','09:00:00','12:00:00'),   -- Chairs
(11,3,2,'Allocated','09:00:00','12:00:00'),     -- Projectors
(11,4,4,'Allocated','09:00:00','12:00:00'),     -- Microphones
(11,8,150,'Allocated','09:00:00','12:00:00'),   -- Lunch Boxes

-- AI in Medicine (Session 12)
(12,1,120,'Allocated','10:00:00','12:00:00'),
(12,3,1,'Allocated','10:00:00','12:00:00'),
(12,4,3,'Allocated','10:00:00','12:00:00'),

-- Live Band Performance (Session 6)
(6,1,200,'Allocated','17:00:00','21:00:00'),
(6,4,6,'Allocated','17:00:00','21:00:00'),
(6,5,2,'Allocated','17:00:00','21:00:00');   -- LED Screens

-- Queries -- 

-- List of all events which are upcoming
SELECT event_name,start_date,venue_id
FROM Event
WHERE event_status='Upcoming';

-- List of all the users that are performers
SELECT u.first_name,u.last_name
FROM Users u
JOIN User_Role ur ON u.user_id=ur.user_id
WHERE ur.role_type='Performer';

-- List of all the attendees of a particular event
SELECT u.first_name,u.last_name, u.phone_no, u.email_id, e.event_name
FROM Users u
JOIN Event_Registration er ON u.user_id=er.user_id
JOIN Event e ON er.event_id=e.event_id
WHERE e.event_name='AI Innovation Summit';

-- List of total revenue earned per event
SELECT e.event_name,SUM(p.amount) AS total_revenue
FROM Event e
JOIN Event_Registration er ON e.event_id=er.event_id
JOIN Payment p ON er.registration_id=p.registration_id
WHERE p.payment_status='Success'
GROUP BY e.event_name;

-- Vendors list with a list of all the stationery each vendor has
SELECT v.vendor_name,vm.material_name
FROM Vendor v
JOIN Vendor_Material vm ON v.vendor_id=vm.vendor_id
WHERE v.vendor_type='Stationery';

-- Events that still have slots left
SELECT event_name
FROM Event
WHERE available_slots>0;

-- List of event and it's registrations 
SELECT event_name,total_registrations
FROM Event
ORDER BY total_registrations DESC;

-- Event with maximum registration/ most popular event
SELECT event_name,total_registrations
FROM Event
ORDER BY total_registrations DESC
LIMIT 1;

-- List of users attending more than 1 session 
SELECT u.first_name,COUNT(er.session_id) AS total_sessions
FROM Users u
JOIN Session_Registration er ON u.user_id=er.user_id
GROUP BY u.user_id
HAVING COUNT(er.session_id)>1;

-- List of revenue generated by city 
SELECT v.city,SUM(p.amount) AS city_revenue
FROM Payment p
JOIN Event_Registration er ON p.registration_id=er.registration_id
JOIN Event e ON er.event_id=e.event_id
JOIN Venue v ON e.venue_id=v.venue_id
GROUP BY v.city;

-- List of vendors that allow courier facilty
SELECT vendor_name,city
FROM Vendor
WHERE courier_facility=TRUE;

-- List showing each event, it's venue, total registration and revenue generated
SELECT e.event_name, v.venue_name,
COUNT(er.registration_id) AS total_registrations,
SUM(p.amount) AS total_revenue
FROM Event e
JOIN Venue v ON e.venue_id=v.venue_id
LEFT JOIN Event_Registration er ON e.event_id=er.event_id
LEFT JOIN Payment p ON er.registration_id=p.registration_id
GROUP BY e.event_id;

-- List of all resources used for a particular sesion
SELECT s.title, r.resource_name, ra.quantity_allocated
FROM Session s
JOIN Resource_Allocation ra ON s.session_id = ra.session_id
JOIN Resource r ON ra.resource_id = r.resource_id
WHERE s.session_id = 11;

-- List of total resources used per event 
SELECT e.event_name, r.resource_name,
SUM(ra.quantity_allocated) AS total_used
FROM Event e
JOIN Session s ON e.event_id = s.event_id
JOIN Resource_Allocation ra ON s.session_id = ra.session_id
JOIN Resource r ON ra.resource_id = r.resource_id
GROUP BY e.event_name, r.resource_name;

-- List of vendors that are in Delhi and provide courier facility
SELECT vendor_name, vendor_type
FROM Vendor
WHERE city = 'Delhi'
AND courier_facility = TRUE;

-- List of all food vendors and their menu item 
SELECT v.vendor_name, vm.material_name, vm.price
FROM Vendor 
JOIN Vendor_Material vm ON v.vendor_id = vm.vendor_id
WHERE v.vendor_type = 'Food';

Use Dbms_Project;
show columns from Event_registration;

select * from Venue;
select * from Event;

ALTER TABLE Users
ADD username VARCHAR(50) UNIQUE;

