-- ================================================================
-- 1. Create Database and Switch Context (Optional)
-- ================================================================
-- CREATE DATABASE MarineData;
-- \c MarineData;

-- ================================================================
-- 2. Reference Tables
-- ================================================================

-- 2.1 SFI Code Reference
CREATE TABLE IF NOT EXISTS SFI_CodeReference (
    sfi_code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(255)
);

-- 2.2 Equipment Category
CREATE TABLE IF NOT EXISTS EquipmentCategory (
    equipment_category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE  -- e.g. "Propulsion", "Navigation", "Electrical"
);

-- 2.3 Equipment Type
CREATE TABLE IF NOT EXISTS EquipmentType (
    equipment_type_id SERIAL PRIMARY KEY,
    equipment_category_id INT NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (equipment_category_id) 
        REFERENCES EquipmentCategory(equipment_category_id)
);

-- 2.4 Hull Type
CREATE TABLE IF NOT EXISTS HullType (
    hull_type_id SERIAL PRIMARY KEY,
    hull_type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 2.5 Propulsion Type
CREATE TABLE IF NOT EXISTS PropulsionType (
    propulsion_type_id SERIAL PRIMARY KEY,
    propulsion_type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 2.6 Navigation System Type
CREATE TABLE IF NOT EXISTS NavigationSystemType (
    navigation_system_type_id SERIAL PRIMARY KEY,
    system_type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 2.7 Safety System Type
CREATE TABLE IF NOT EXISTS SafetySystemType (
    safety_system_type_id SERIAL PRIMARY KEY,
    system_type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 2.8 Instrumentation System Type
CREATE TABLE IF NOT EXISTS InstrumentationSystemType (
    instrumentation_system_type_id SERIAL PRIMARY KEY,
    system_type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 2.9 Electrical System Type
CREATE TABLE IF NOT EXISTS ElectricalSystemType (
    electrical_system_type_id SERIAL PRIMARY KEY,
    system_type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- 2.10 Certificate Type
CREATE TABLE IF NOT EXISTS CertificateType (
    certificate_type_id SERIAL PRIMARY KEY,
    certificate_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- 2.11 Survey Type
CREATE TABLE IF NOT EXISTS SurveyType (
    survey_type_id SERIAL PRIMARY KEY,
    survey_type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- ================================================================
-- 3. Main Domain Tables
-- ================================================================

-- 3.1 Ship
CREATE TABLE IF NOT EXISTS Ship (
    ship_id SERIAL PRIMARY KEY,
    ship_name VARCHAR(100) NOT NULL,
    imo_number VARCHAR(20) UNIQUE,
    mmsi VARCHAR(9) UNIQUE,
    call_sign VARCHAR(10),
    flag_state VARCHAR(100),
    port_of_registry VARCHAR(100),
    classification_society VARCHAR(100),
    ship_type VARCHAR(50),  -- e.g. "Tanker", "Bulk Carrier"
    build_year INT,
    build_yard VARCHAR(100),
    owner VARCHAR(255),
    operator VARCHAR(255)
);

-- 3.2 ShipHull
CREATE TABLE IF NOT EXISTS ShipHull (
    hull_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    hull_type_id INT NOT NULL,
    tonnage NUMERIC(10,2),
    length NUMERIC(10,2),
    crew INT,
    cargo_capacity NUMERIC(10,2),
    general_hull_shape VARCHAR(100),
    gross_tonnage NUMERIC(10,2),
    net_tonnage NUMERIC(10,2),
    deadweight_tonnage NUMERIC(10,2),
    beam NUMERIC(10,2),
    draft NUMERIC(10,2),
    depth NUMERIC(10,2),
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (hull_type_id) REFERENCES HullType(hull_type_id)
);

-- 3.3 Superstructure
CREATE TABLE IF NOT EXISTS Superstructure (
    superstructure_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    bridge VARCHAR(100),
    access_ways VARCHAR(100),
    deck_layout VARCHAR(100),
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id)
);

-- 3.4 PropulsionSystem
CREATE TABLE IF NOT EXISTS PropulsionSystem (
    propulsion_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    propulsion_type_id INT NOT NULL,
    fuel_consumption NUMERIC(10,2),
    speed NUMERIC(10,2),
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (propulsion_type_id) REFERENCES PropulsionType(propulsion_type_id)
);

-- 3.5 ElectricalSystem
CREATE TABLE IF NOT EXISTS ElectricalSystem (
    electrical_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    electrical_system_type_id INT NOT NULL,
    power_generation VARCHAR(100),
    distribution VARCHAR(100),
    voltage NUMERIC(10,2),
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (electrical_system_type_id) REFERENCES ElectricalSystemType(electrical_system_type_id)
);

-- 3.6 NavigationSystem
CREATE TABLE IF NOT EXISTS NavigationSystem (
    navigation_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    navigation_system_type_id INT NOT NULL,
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (navigation_system_type_id) REFERENCES NavigationSystemType(navigation_system_type_id)
);

-- 3.7 SafetySystem
CREATE TABLE IF NOT EXISTS SafetySystem (
    safety_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    safety_system_type_id INT NOT NULL,
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (safety_system_type_id) REFERENCES SafetySystemType(safety_system_type_id)
);

-- 3.8 InstrumentationControlSystem
CREATE TABLE IF NOT EXISTS InstrumentationControlSystem (
    instrumentation_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    instrumentation_system_type_id INT NOT NULL,
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (instrumentation_system_type_id) REFERENCES InstrumentationSystemType(instrumentation_system_type_id)
);

-- 3.9 Certificate
CREATE TABLE IF NOT EXISTS Certificate (
    certificate_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    certificate_type_id INT NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE,
    issuing_authority VARCHAR(100),
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (certificate_type_id) REFERENCES CertificateType(certificate_type_id)
);

-- 3.10 Survey
CREATE TABLE IF NOT EXISTS Survey (
    survey_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    survey_type_id INT NOT NULL,
    survey_date DATE,
    result VARCHAR(50),
    remarks TEXT,
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (survey_type_id) REFERENCES SurveyType(survey_type_id)
);

-- ================================================================
-- 4. Equipment Normalization and Logs
-- ================================================================

-- 4.1 EquipmentInstance
CREATE TABLE IF NOT EXISTS EquipmentInstance (
    equipment_instance_id SERIAL PRIMARY KEY,
    ship_id INT NOT NULL,
    equipment_type_id INT NOT NULL,
    system_id INT,           -- Optionally link to e.g. PropulsionSystem, if desired
    serial_number VARCHAR(100),
    installation_date DATE,
    configuration JSON,      -- or use JSONB if you prefer
    FOREIGN KEY (ship_id) REFERENCES Ship(ship_id),
    FOREIGN KEY (equipment_type_id) REFERENCES EquipmentType(equipment_type_id)
);

-- 4.2 EquipmentOperations
CREATE TABLE IF NOT EXISTS EquipmentOperations (
    operation_id SERIAL PRIMARY KEY,
    equipment_instance_id INT NOT NULL,
    state VARCHAR(50) NOT NULL,  -- e.g., 'Operational', 'Under Maintenance'
    status VARCHAR(50),
    configuration JSON,          -- or JSONB
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_instance_id) REFERENCES EquipmentInstance(equipment_instance_id)
);

-- 4.3 MaintenanceInspectionLog
CREATE TABLE IF NOT EXISTS MaintenanceInspectionLog (
    log_id SERIAL PRIMARY KEY,
    equipment_instance_id INT NOT NULL,
    log_type VARCHAR(50) NOT NULL,  -- e.g. 'Maintenance', 'Inspection'
    description TEXT,
    performed_by VARCHAR(100),
    log_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    next_due_date TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (equipment_instance_id) REFERENCES EquipmentInstance(equipment_instance_id)
);

-- 4.4 MaintenanceTask
CREATE TABLE IF NOT EXISTS MaintenanceTask (
    task_id SERIAL PRIMARY KEY,
    equipment_instance_id INT NOT NULL,
    description TEXT,
    frequency_days INT,
    last_completed DATE,
    next_due DATE,
    FOREIGN KEY (equipment_instance_id) REFERENCES EquipmentInstance(equipment_instance_id)
);
