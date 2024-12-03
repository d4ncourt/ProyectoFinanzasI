Use PEYADB;

-- Tabla para registrar los parámetros de entrada
CREATE TABLE Parametros (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    CostosFijos FLOAT NOT NULL,
    PrecioPorUnidad FLOAT NOT NULL,
    CostoVariablePorUnidad FLOAT NOT NULL,
    FechaRegistro DATETIME DEFAULT GETDATE()
);

-- Tabla para almacenar los resultados calculados
CREATE TABLE Resultados (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    PuntoEquilibrioUnidades FLOAT NOT NULL,
    PuntoEquilibrioIngresos FLOAT NOT NULL,
    Apalancamiento FLOAT NOT NULL,
    ParametroID INT FOREIGN KEY REFERENCES Parametros(ID),
    FechaCalculo DATETIME DEFAULT GETDATE()
);


INSERT INTO Parametros (CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad)
VALUES (5000, 20, 10);

INSERT INTO Resultados (PuntoEquilibrioUnidades, PuntoEquilibrioIngresos, Apalancamiento, ParametroID)
VALUES (500, 10000, 1.5, 1);

SELECT * From Parametros
Select * From Resultados


ALTER TABLE Parametros
ADD VentasTotales FLOAT NULL,
    Intereses FLOAT NULL;


INSERT INTO Parametros (CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad, VentasTotales, Intereses)
VALUES 
    (5000, 50, 30, 10000, 200), -- Registro de prueba 1
    (10000, 60, 40, 15000, 300); -- Registro de prueba 2


UPDATE Parametros
SET VentasTotales = 0,  
    Intereses = 0;      


ALTER TABLE Parametros
ALTER COLUMN VentasTotales FLOAT NOT NULL;

ALTER TABLE Parametros
ALTER COLUMN Intereses FLOAT NOT NULL;



ALTER TABLE Resultados
ADD ApalancamientoOperativo FLOAT NULL,
    ApalancamientoFinanciero FLOAT NULL;

UPDATE Resultados
SET ApalancamientoOperativo = 0,  -- Cambia 0 por el valor que necesites
    ApalancamientoFinanciero = 0; 

ALTER TABLE Resultados
ALTER COLUMN ApalancamientoOperativo FLOAT NOT NULL;

ALTER TABLE Resultados
ALTER COLUMN ApalancamientoFinanciero FLOAT NOT NULL;

INSERT INTO Parametros (CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad, VentasTotales, Intereses)
VALUES (5000, 100, 50, 100000, 2000);


ALTER TABLE Parametros
ADD VentasTotales FLOAT NULL,
    Intereses FLOAT NULL;

	INSERT INTO Parametros (ID, CostosFijos, PrecioPorUnidad, CostoVariablePorUnidad, VentasTotales, Intereses)
VALUES (1000, 50, 10, 0, 0);

ALTER TABLE Parametros
ALTER COLUMN VentasTotales DECIMAL(10,2) NULL;

ALTER TABLE Parametros
ALTER COLUMN Intereses DECIMAL(10,2) NULL;
