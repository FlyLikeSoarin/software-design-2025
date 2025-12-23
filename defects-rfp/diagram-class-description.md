## Описание диаграммы классов

Диаграмма классов описывает модель данных для управления **автомобилями**, **дефектами**, **ремонтными задачами**, **ремонтными ресурсами (зоны/места)**, а также **персоналом**, его **сменной доступностью** и **результатами QC-испытаний**.

---

### Основные сущности

#### Vehicle (Автомобиль)

Хранит данные об автомобиле и его текущем статусе.

- `vehicleId: UUID` - идентификатор авто
- `vin, configCode, color` - атрибуты
- `status: VehicleStatus` - статус жизненного цикла (например: `InProduction`, `InRepair`, `InQC`, `Shipped`)

#### Defect (Дефект)

Факт обнаружения дефекта на конкретном автомобиле.

- `defectId: UUID`
- `vehicleId: UUID` - ссылка на авто
- `detectedAt: DateTime` - когда найден
- `stage: StageCode` - этап, на котором выявлен (например: `Body`, `Paint`, `Assembly`, `QC`, …)
- `locationMark: String` - место/метка на кузове или узле
- `cause: DefectCause` - тип причины (например: `Mechanical`, `Electrical`, `Paint`, `Assembly`, …)
- `notes: String` - комментарии
- `reportedById: UUID` - кто зарегистрировал (инспектор/QC)

#### RepairTask (Ремонтная задача)

Конкретная работа по устранению дефекта.

- `repairId: UUID`
- `defectId: UUID` - к какому дефекту относится
- `zoneId: UUID`, `bayId: UUID` - где ремонт выполняется
- `assignedToId: UUID` - исполнитель (ремонтник)
- `assignedById: UUID` - кто назначил (бригадир/диспетчер)
- `startTime`, `endTime: DateTime` - фактическое время выполнения
- `result: RepairResult` - результат (`Fixed`, `ReworkNeeded`, `Aborted`)

#### RepairZone / RepairBay (Ремонтная зона / Место ремонта)

Описывает ремонтную инфраструктуру.

- **RepairZone**: `zoneId`, `name`, `section`, …
- **RepairBay**: `bayId`, `zoneId`, `label`, `isActive`

#### Employee / Crew (Сотрудник / Бригада)

Описывает людей и организацию работ.

- **Employee**: `employeeId`, `fullName`, `role: EmployeeRole`, `crewId`, `isActive`
- **Crew**: `crewId`, `name`, `foremanId`

#### Availability (Доступность сотрудника)

Фиксирует статус доступности сотрудника на дату/смену.

- `availabilityId`, `employeeId`
- `date: Date`, `shiftCode: String`
- `status: AvailabilityStatus` (`Available`, `Busy`, `Off`)

#### QCTest (QC-испытание)

Результаты контроля качества по автомобилю.

- `testId`, `vehicleId`
- `type: QCTestType` (`Stand`, `Road`)
- `performedAt: DateTime`
- `result: QCTestResult` (`Pass`, `Fail`)
- `notes: String`

---

### Связи и кратности (multiplicity)

- **Vehicle 1 → 0..\*** **Defect** : `has`  
  Один автомобиль может иметь много дефектов (или ни одного).

- **Defect 1 → 1..\*** **RepairTask** : `leadsTo`  
  Каждый дефект приводит минимум к одной ремонтной задаче (включая повторные ремонты/доработки).

- **RepairZone 1 → 1..\*** **RepairBay** : `has`  
  В каждой зоне есть одно или несколько ремонтных мест.

- **RepairTask 1 → 1 RepairZone** : `in`  
  Задача выполняется в конкретной зоне.

- **RepairTask 1 → 1 RepairBay** : `at`  
  Задача привязана к конкретному месту ремонта.

- **Employee 1 → 0..\*** **RepairTask** : `assignedTo`  
  Один сотрудник может быть исполнителем многих задач.

- **Employee 1 → 0..\*** **RepairTask** : `assignedBy`  
  Один сотрудник (например, бригадир/диспетчер) может назначать множество задач.

- **Crew 1 → 1 Employee** : `foreman`  
  У бригады один бригадир.

- **Crew 1 → 0..\*** **Employee** : `members`  
  В бригаде может быть много сотрудников.

- **Employee 1 → 0..\*** **Availability** : `checkins`  
  Сотрудник имеет множество отметок доступности по сменам/датам.

- **Vehicle 1 → 0..\*** **QCTest** : `testedByQC`  
  Авто может проходить несколько испытаний (стенд/дорога, повторные проверки).

---

### Логика модели (кратко)

Автомобиль (**Vehicle**) в ходе производства и контроля качества может получить один или несколько дефектов (**Defect**). Каждый дефект приводит к созданию одной или нескольких ремонтных задач (**RepairTask**), которые назначаются сотрудникам (**Employee**) и выполняются в конкретной ремонтной зоне/месте (**RepairZone/RepairBay**). Смена и доступность сотрудников учитывается через **Availability**. После ремонта автомобиль проходит испытания (**QCTest**), результат которых влияет на дальнейшие действия (Pass/Fail, повторный ремонт и т.п.).
