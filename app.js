// ============ DATA ============
let students = [];

let currentUser = null;
let currentLevel = 'primaria_prescolar';
let currentTab = 'inicio';

const levelNames = {
  primaria: 'Primaria',
  prescolar: 'Preescolar',
  primaria_prescolar: 'Primaria/Preescolar',
  bachillerato: 'Bachillerato'
};

// ============ DOM REFS ============
const $ = id => document.getElementById(id);
const loginScreen = $('loginScreen');
const dashboardScreen = $('dashboardScreen');
const loginForm = $('loginForm');
const registerForm = $('registerForm');
const loginError = $('loginError');
const registerError = $('registerError');
const registerSuccess = $('registerSuccess');
const searchInput = $('searchInput');
const studentsBody = $('studentsTableBody');
const searchBody = $('searchResultsBody');
const searchEmpty = $('searchEmpty');
const studentsEmpty = $('studentsEmpty');
const levelsBody = $('levelsTableBody');
const levelsEmpty = $('levelsEmpty');
const resultCount = $('resultCount');
const currentLevelSpan = $('currentLevel');
const dashboardTitle = $('dashboardTitle');
const addStudentScreen = $('addStudentScreen');
const studentForm = $('studentForm');
const hamburger = $('hamburger');
const sidebar = $('sidebar');

// ============ AUTH TABS ============
document.querySelectorAll('.auth-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
    tab.classList.add('active');
    $(tab.dataset.form + 'Form').classList.add('active');
    loginError.classList.remove('show');
    registerError.classList.remove('show');
    registerSuccess.classList.remove('show');
  });
});

// ============ LOGIN ============
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = $('username').value.trim();
  const password = $('password').value.trim();

  const response = await eel.login(username, password)();
  
  if (response.success) {
    currentUser = response.user;
    loginSuccess();
  } else {
    loginError.textContent = response.error || 'Usuario o contraseña incorrectos';
    loginError.classList.add('show');
  }
});

function loginSuccess() {
  loginError.classList.remove('show');
  currentLevel = currentUser.isAdmin ? 'primaria_prescolar' : currentUser.level;
  showScreen('dashboard');
  currentTab = 'inicio';
  updateSidebarUser();
  applyPermissions();
  renderDashboard();
}

// ============ REGISTER ============
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = $('regUser').value.trim();
  const password = $('regPass').value.trim();
  const confirm = $('regPassConfirm').value.trim();
  const level = $('regLevel').value;

  registerError.classList.remove('show');
  registerSuccess.classList.remove('show');

  if (!username || !password || !confirm) {
    registerError.textContent = 'Completa todos los campos';
    registerError.classList.add('show');
    return;
  }

  if (password !== confirm) {
    registerError.textContent = 'Las contraseñas no coinciden';
    registerError.classList.add('show');
    return;
  }

  if (password.length < 4) {
    registerError.textContent = 'La contraseña debe tener al menos 4 caracteres';
    registerError.classList.add('show');
    return;
  }

  const response = await eel.register(username, password, level)();

  if (response.success) {
    registerForm.reset();
    registerSuccess.classList.add('show');
    setTimeout(() => {
      registerSuccess.classList.remove('show');
      document.querySelector('.auth-tab[data-form="login"]').click();
      $('username').value = username;
      $('password').value = password;
    }, 1500);
  } else {
    registerError.textContent = response.error || 'Error al registrar';
    registerError.classList.add('show');
  }
});

// ============ SCREEN NAV ============
function showScreen(screen) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  if (screen === 'login') loginScreen.classList.add('active');
  if (screen === 'dashboard') dashboardScreen.classList.add('active');
}

// ============ SIDEBAR USER ============
function updateSidebarUser() {
  $('sidebarUserName').textContent = currentUser.username;
  $('sidebarUserLevel').textContent = currentUser.isAdmin
    ? 'Administrador'
    : levelNames[currentUser.level];
}

function populateStudentLevelDropdown() {
  const sLevel = $('sLevel');
  if (!sLevel) return;
  const isAdmin = currentUser.isAdmin;
  const userLvl = currentUser.level;
  
  let options = '';
  if (isAdmin) {
    options = `
      <option value="prescolar">Preescolar</option>
      <option value="primaria">Primaria</option>
      <option value="bachillerato">Bachillerato</option>
    `;
  } else if (userLvl === 'primaria_prescolar') {
    options = `
      <option value="prescolar">Preescolar</option>
      <option value="primaria">Primaria</option>
    `;
  } else {
    options = `
      <option value="bachillerato">Bachillerato</option>
    `;
  }
  sLevel.innerHTML = options;
  
  if (currentLevel === 'primaria_prescolar') {
    sLevel.value = 'primaria';
  } else {
    sLevel.value = currentLevel;
  }
}

function applyPermissions() {
  const isAdmin = currentUser.isAdmin;
  const userLvl = currentUser.level;

  // Ocultar pestaña "Niveles" si no es admin
  const nivelesNav = document.querySelector('.nav-item[data-tab="niveles"]');
  if (nivelesNav) {
    nivelesNav.style.display = isAdmin ? 'flex' : 'none';
  }

  // Filtrar botones de acceso rápido
  document.querySelectorAll('.welcome-level-btn').forEach(btn => {
    if (!isAdmin && btn.dataset.level !== userLvl) {
      btn.style.display = 'none';
    } else {
      btn.style.display = 'inline-flex';
    }
  });

  // Filtrar tarjetas de estadísticas
  ['primaria_prescolar', 'bachillerato'].forEach(lvl => {
    const statCount = document.getElementById('count-' + lvl);
    if (statCount) {
      const card = statCount.closest('.stat-card');
      if (card) {
        if (!isAdmin && lvl !== userLvl) {
          card.style.display = 'none';
        } else {
          card.style.display = 'flex';
        }
      }
    }
  });

  // Configurar el selector de nivel al agregar un alumno
  populateStudentLevelDropdown();
}

// ============ DASHBOARD ============
async function renderDashboard() {
  currentLevelSpan.textContent = levelNames[currentLevel];
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const tabEl = document.getElementById('tab-' + currentTab);
  if (tabEl) tabEl.classList.add('active');

  const navEl = document.querySelector(`.nav-item[data-tab="${currentTab}"]`);
  if (navEl) navEl.classList.add('active');

  dashboardTitle.textContent = currentTab === 'inicio' ? 'Inicio' : currentTab === 'alumnos' ? 'Alumnos' : 'Niveles';

  students = await eel.get_alumnos(null)();
  populateFilterAnios();

  updateCounts();
  renderStudents();
  renderLevelsTable();
  handleSearch();

  document.querySelectorAll('.level-tab').forEach(t => t.classList.remove('active'));
  const activeLevelTab = document.querySelector(`.level-tab[data-level="${currentLevel}"]`);
  if (activeLevelTab) activeLevelTab.classList.add('active');
}

function updateCounts() {
  const countPrimariaPrescolar = students.filter(s => s.level === 'primaria' || s.level === 'prescolar').length;
  const countBachillerato = students.filter(s => s.level === 'bachillerato').length;
  
  const elPP = document.getElementById('count-primaria_prescolar');
  if (elPP) elPP.textContent = countPrimariaPrescolar;
  
  const elBach = document.getElementById('count-bachillerato');
  if (elBach) elBach.textContent = countBachillerato;
}

// ============ WELCOME LEVEL BTNS ============
document.querySelectorAll('.welcome-level-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    currentLevel = btn.dataset.level;
    currentTab = 'alumnos';
    renderDashboard();
  });
});

// ============ STUDENTS TABLE ============
function renderStudents() {
  const q = searchInput.value.trim().toLowerCase();
  const filtered = students.filter(s => {
    const matchesLevel = (currentLevel === 'primaria_prescolar') 
      ? (s.level === 'primaria' || s.level === 'prescolar') 
      : (s.level === currentLevel);
    return matchesLevel &&
      (!q || s.nombre.toLowerCase().includes(q) || s.apellido.toLowerCase().includes(q) || s.cedula.toLowerCase().includes(q) || (s.anios && s.anios.some(a => a.toLowerCase().includes(q))));
  });

  if (filtered.length === 0) {
    studentsBody.innerHTML = '';
    studentsEmpty.style.display = 'block';
    return;
  }
  studentsEmpty.style.display = 'none';
  studentsBody.innerHTML = filtered.map(s => `
    <tr>
      <td><strong>${s.nombre}</strong></td>
      <td>${s.apellido}</td>
      <td>${levelNames[s.level]}</td>
      <td>${s.cedula}</td>
      <td>
        <button onclick="openPerfil(${s.id})" style="background:none;border:none;cursor:pointer;color:#4f46e5;font-size:1.2rem;" title="Ver perfil"><i class="fa-solid fa-eye"></i></button>
      </td>
    </tr>
  `).join('');

  document.querySelectorAll('#studentsTableBody .btn-delete').forEach(btn => {
    btn.addEventListener('click', () => deleteStudent(btn.dataset.id));
  });
}

function populateFilterAnios() {
  const select = $('filterAnio');
  if (!select) return;
  const currentVal = select.value;
  
  const yearsSet = new Set();
  students.forEach(s => {
    if (s.anios) {
      s.anios.forEach(yr => {
        if (yr && yr.trim()) yearsSet.add(yr.trim());
      });
    }
  });
  
  const sortedYears = Array.from(yearsSet).sort((a,b) => b - a);
  select.innerHTML = '<option value="todos">Todos los Años</option>' + 
    sortedYears.map(yr => `<option value="${yr}">${yr}</option>`).join('');
  
  if (currentVal && sortedYears.includes(currentVal)) {
    select.value = currentVal;
  } else {
    select.value = 'todos';
  }
}

// ============ SEARCH ============
function handleSearch() {
  const q = searchInput.value.trim().toLowerCase();
  const lvlFilter = $('filterNivel') ? $('filterNivel').value : 'todos';
  const yrFilter = $('filterAnio') ? $('filterAnio').value : 'todos';

  if (!q && lvlFilter === 'todos' && yrFilter === 'todos') {
    searchBody.innerHTML = '';
    searchEmpty.style.display = 'block';
    searchEmpty.querySelector('p').textContent = 'Busca alumnos por nombre, apellido o matrícula';
    resultCount.textContent = '0 alumnos';
  } else {
    const results = students.filter(s => {
      const matchesQuery = !q ||
        s.nombre.toLowerCase().includes(q) ||
        s.apellido.toLowerCase().includes(q) ||
        s.cedula.toLowerCase().includes(q) ||
        (s.anios && s.anios.some(a => a.toLowerCase().includes(q)));
        
      const matchesLvl = lvlFilter === 'todos' || s.level === lvlFilter;
      const matchesYr = yrFilter === 'todos' || (s.anios && s.anios.includes(yrFilter));
      
      return matchesQuery && matchesLvl && matchesYr;
    });

    resultCount.textContent = `${results.length} alumno${results.length !== 1 ? 's' : ''}`;

    if (results.length === 0) {
      searchBody.innerHTML = '';
      searchEmpty.style.display = 'block';
      searchEmpty.querySelector('p').textContent = 'No se encontraron alumnos';
    } else {
      searchEmpty.style.display = 'none';
      searchBody.innerHTML = results.map(s => `
        <tr>
          <td><strong>${s.nombre}</strong></td>
          <td>${s.apellido}</td>
          <td>${levelNames[s.level]}</td>
          <td>${s.cedula}</td>
          <td>
            <button onclick="openPerfil(${s.id})" style="background:none;border:none;cursor:pointer;color:#4f46e5;font-size:1.2rem;" title="Ver perfil"><i class="fa-solid fa-eye"></i></button>
          </td>
        </tr>
      `).join('');
    }
  }

  // Aplicar también a las otras tablas
  renderStudents();
  renderLevelsTable();
}

searchInput.addEventListener('input', handleSearch);

const filterNivel = $('filterNivel');
if (filterNivel) {
  filterNivel.addEventListener('change', handleSearch);
}
const filterAnio = $('filterAnio');
if (filterAnio) {
  filterAnio.addEventListener('change', handleSearch);
}

// ============ LEVELS TABLE ============
function renderLevelsTable() {
  const q = searchInput.value.trim().toLowerCase();
  const filtered = students.filter(s => {
    const matchesLevel = (currentLevel === 'primaria_prescolar') 
      ? (s.level === 'primaria' || s.level === 'prescolar') 
      : (s.level === currentLevel);
    return matchesLevel &&
      (!q || s.nombre.toLowerCase().includes(q) || s.apellido.toLowerCase().includes(q) || s.cedula.toLowerCase().includes(q) || (s.anios && s.anios.some(a => a.toLowerCase().includes(q))));
  });

  if (filtered.length === 0) {
    levelsBody.innerHTML = '';
    levelsEmpty.style.display = 'block';
    return;
  }
  levelsEmpty.style.display = 'none';
  levelsBody.innerHTML = filtered.map(s => `
    <tr>
      <td><strong>${s.nombre}</strong></td>
      <td>${s.apellido}</td>
      <td>${s.cedula}</td>
      <td>
        <button onclick="openPerfil(${s.id})" style="background:none;border:none;cursor:pointer;color:#4f46e5;font-size:1.2rem;" title="Ver perfil"><i class="fa-solid fa-eye"></i></button>
      </td>
    </tr>
  `).join('');

  document.querySelectorAll('#levelsTableBody .btn-delete').forEach(btn => {
    btn.addEventListener('click', () => deleteStudent(btn.dataset.id));
  });
}

document.querySelectorAll('.level-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.level-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentLevel = tab.dataset.level;
    currentLevelSpan.textContent = levelNames[currentLevel];
    renderLevelsTable();
  });
});

// ============ NAVIGATION ============
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    currentTab = item.dataset.tab;
    if (currentTab === 'inicio') {
      currentLevelSpan.textContent = levelNames[currentLevel];
    }
    renderDashboard();
    if (window.innerWidth <= 768) sidebar.classList.remove('open');
  });
});

// ============ LOGOUT ============
$('logoutBtn').addEventListener('click', () => {
  currentUser = null;
  showScreen('login');
  $('username').value = '';
  $('password').value = '';
  loginError.classList.remove('show');
  document.querySelector('.auth-tab[data-form="login"]').click();
});

// ============ ADD STUDENT SCREEN ============
function openAddStudentScreen() {
  addStudentScreen.style.display = 'block';
  studentForm.reset();
  populateStudentLevelDropdown();
  $('sId').value = '';
  $('sTipo').value = 'Regular';
  $('sIngresoPeriodoGroup').style.display = 'block';
  populateIngresoPeriodoDropdown();
  renderNotasModal($('sLevel').value);
  // Reset familiares
  const cont = $('familiaresContainer');
  cont.innerHTML = '<p style="color:#9ca3af;font-size:0.88rem;text-align:center;padding:16px 0;" id="noFamiliaresMsg">Haz clic en "Agregar Familiar" para añadir un representante.</p>';
  // Scroll to top
  addStudentScreen.scrollTop = 0;
}

function closeAddStudentScreen() {
  addStudentScreen.style.display = 'none';
}

$('addStudentBtn').addEventListener('click', openAddStudentScreen);

// Re-render notes when level changes inside the modal
$('sLevel').addEventListener('change', function() {
  populateIngresoPeriodoDropdown();
  renderNotasModal(this.value);
});

// Handle type changes inside the modal
$('sTipo').addEventListener('change', function() {
  if (this.value === 'Nuevo Ingreso' || this.value === 'Regular') {
    $('sIngresoPeriodoGroup').style.display = 'block';
    populateIngresoPeriodoDropdown();
  } else {
    $('sIngresoPeriodoGroup').style.display = 'none';
  }
  renderNotasModal($('sLevel').value);
});

$('sIngresoPeriodo').addEventListener('change', function() {
  renderNotasModal($('sLevel').value);
});

function populateIngresoPeriodoDropdown() {
  const nivel = $('sLevel').value;
  const dropdown = $('sIngresoPeriodo');
  const perList = periodos[nivel] || [];
  dropdown.innerHTML = perList.map(p => `<option value="${p}">${p}</option>`).join('');
}

function renderNotasModal(nivel) {
  const grid = $('notasFilesGrid');
  const tipo = $('sTipo').value;
  const ingresoPeriodo = $('sIngresoPeriodo').value;
  const perList = periodos[nivel] || [];
  grid.innerHTML = '';
  
  // Decide which periods to display
  let periodsToShow = [];
  if (tipo === 'Egresado') {
    periodsToShow = ['Notas Totales'];
  } else if (tipo === 'Nuevo Ingreso' || tipo === 'Regular') {
    const idx = perList.indexOf(ingresoPeriodo);
    if (idx > 0) {
      periodsToShow = [perList[idx - 1]];
    } else {
      const seqIdx = sequenceOfPeriodos.indexOf(ingresoPeriodo);
      if (seqIdx > 0) {
        periodsToShow = [sequenceOfPeriodos[seqIdx - 1]];
      } else {
        periodsToShow = [];
      }
    }
  }
  
  if (periodsToShow.length === 0) {
    grid.innerHTML = `
      <div style="padding:15px;text-align:center;color:#6b7280;background:#f3f4f6;border-radius:10px;font-size:0.9rem;">
        No se requieren notas del año anterior para este grado.
      </div>`;
    return;
  }
  
  periodsToShow.forEach(p => {
    const safeId = 'addfile_' + p.replace(/[^a-zA-Z0-9]/g, '_');
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;';
    row.innerHTML = `
      <span style="font-weight:500;color:#374151;font-size:0.9rem;">${p}</span>
      <div style="display:flex;align-items:center;gap:10px;">
        <input type="text" id="${safeId}_anio" placeholder="Año (ej. 2023)" style="width:100px;padding:4px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:0.85rem;" value="${new Date().getFullYear()}">
        <label for="${safeId}" style="display:inline-flex;align-items:center;gap:6px;cursor:pointer;">
          <input type="file" id="${safeId}" data-periodo="${p}" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" style="display:none;">
          <span id="${safeId}_label" style="font-size:0.82rem;color:#6b7280;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">Sin archivo</span>
          <span style="background:#4f46e5;color:white;border:none;padding:5px 12px;border-radius:7px;font-size:0.8rem;">
            <i class="fas fa-paperclip"></i> Adjuntar
          </span>
        </label>
      </div>
    `;
    
    // Update label text when file picked
    const inputEl = row.querySelector(`#${safeId}`);
    inputEl.addEventListener('change', function() {
      const lbl = $(`${safeId}_label`);
      if (this.files[0]) {
        lbl.textContent = this.files[0].name;
        lbl.style.color = '#10b981';
      } else {
        lbl.textContent = 'Sin archivo';
        lbl.style.color = '#6b7280';
      }
    });
    grid.appendChild(row);
  });
}

// No close/cancel for modal anymore — handled by closeAddStudentScreen()

studentForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const newStudent = {
    cedula: $('sId').value.trim(),
    nombre: $('sName').value.trim(),
    apellido: $('sLastName').value.trim(),
    nivel: $('sLevel').value
  };

  if (!newStudent.nombre || !newStudent.apellido || !newStudent.cedula) return;

  const tipo = $('sTipo').value;
  const ingreso_periodo = (tipo === 'Nuevo Ingreso' || tipo === 'Regular') ? $('sIngresoPeriodo').value : null;
  const direccion = $('sDireccion').value.trim() || null;
  const ciudad = $('sCiudad').value.trim() || null;
  const estado_residencia = $('sEstadoResidencia').value.trim() || null;
  const telefono_casa = $('sTelefonoCasa').value.trim() || null;

  // Collect files before saving
  const fileInputs = $('notasFilesGrid').querySelectorAll('input[type="file"]');
  const filesToUpload = [];
  for (const inp of fileInputs) {
    if (inp.files[0]) {
      const anioInput = document.getElementById(inp.id + '_anio');
      const anio = anioInput ? anioInput.value.trim() : '';
      filesToUpload.push({ periodo: inp.dataset.periodo, file: inp.files[0], anio: anio || new Date().getFullYear().toString() });
    }
  }

  // Collect familiares
  const familiarRows = $('familiaresContainer').querySelectorAll('.familiar-row');
  const familiares = [];
  familiarRows.forEach(row => {
    const inputs = row.querySelectorAll('input, select');
    familiares.push({
      nombre:     inputs[0] ? inputs[0].value.trim() : '',
      apellido:   inputs[1] ? inputs[1].value.trim() : '',
      cedula:     inputs[2] ? inputs[2].value.trim() : '',
      telefono:   inputs[3] ? inputs[3].value.trim() : '',
      parentesco: inputs[4] ? inputs[4].value : 'Padre/Madre'
    });
  });

  const saveBtn = $('saveStudentBtn');
  saveBtn.disabled = true;
  saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';

  const response = await eel.add_alumno(
    newStudent.cedula, newStudent.nombre, newStudent.apellido, newStudent.nivel,
    tipo, ingreso_periodo, direccion, ciudad, estado_residencia, telefono_casa
  )();

  if (!response.success) {
    saveBtn.disabled = false;
    saveBtn.innerHTML = '<i class="fas fa-save"></i> Guardar Alumno';
    alert(response.error);
    return;
  }

  const alumnoId = response.id;

  // Save familiares
  if (familiares.length > 0 && alumnoId) {
    await eel.save_familiares(alumnoId, familiares)();
  }

  // Upload files if any
  if (filesToUpload.length > 0 && alumnoId) {
    for (const item of filesToUpload) {
      await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = async function() {
          await eel.upload_nota(alumnoId, item.periodo, reader.result, item.file.name, item.anio)();
          resolve();
        };
        reader.readAsDataURL(item.file);
      });
    }
  }

  saveBtn.disabled = false;
  saveBtn.innerHTML = '<i class="fas fa-save"></i> Guardar Alumno';
  closeAddStudentScreen();
  renderDashboard();
});

let familiarCounter = 0;
function addFamiliarRow() {
  const msg = $('noFamiliaresMsg');
  if (msg) msg.remove();
  const cont = $('familiaresContainer');
  familiarCounter++;
  const div = document.createElement('div');
  div.className = 'familiar-row';
  div.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px;display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr auto;gap:10px;align-items:end;';
  div.innerHTML = `
    <div>
      <label style="font-size:0.8rem;font-weight:600;color:#374151;display:block;margin-bottom:4px;">Nombre</label>
      <input type="text" placeholder="Nombre" style="width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:8px;font-size:0.88rem;box-sizing:border-box;">
    </div>
    <div>
      <label style="font-size:0.8rem;font-weight:600;color:#374151;display:block;margin-bottom:4px;">Apellido</label>
      <input type="text" placeholder="Apellido" style="width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:8px;font-size:0.88rem;box-sizing:border-box;">
    </div>
    <div>
      <label style="font-size:0.8rem;font-weight:600;color:#374151;display:block;margin-bottom:4px;">Cédula</label>
      <input type="text" placeholder="Cédula" style="width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:8px;font-size:0.88rem;box-sizing:border-box;">
    </div>
    <div>
      <label style="font-size:0.8rem;font-weight:600;color:#374151;display:block;margin-bottom:4px;">Teléfono</label>
      <input type="text" placeholder="Número de teléfono" style="width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:8px;font-size:0.88rem;box-sizing:border-box;">
    </div>
    <div>
      <label style="font-size:0.8rem;font-weight:600;color:#374151;display:block;margin-bottom:4px;">Parentesco</label>
      <select style="width:100%;padding:8px 10px;border:1px solid #d1d5db;border-radius:8px;font-size:0.88rem;background:white;">
        <option>Padre/Madre</option>
        <option>Abuelo/a</option>
        <option>Tío/a</option>
        <option>Hermano/a</option>
        <option>Tutor</option>
        <option>Otro</option>
      </select>
    </div>
    <button type="button" onclick="this.closest('.familiar-row').remove()" style="background:#fee2e2;color:#dc2626;border:none;padding:8px 10px;border-radius:8px;cursor:pointer;">
      <i class="fas fa-trash"></i>
    </button>
  `;
  cont.appendChild(div);
}

// ============ DELETE ============
async function deleteStudent(id) {
  if (!confirm('¿Eliminar este alumno y todos sus archivos?')) return;
  const res = await eel.delete_alumno(parseInt(id))();
  if(res.success) {
    renderDashboard();
  } else {
    alert("Error al eliminar: " + res.error);
  }
}

// ============ PERFIL SCREEN ============
const perfilScreen = $('perfilScreen');

function closePerfilScreen() {
  perfilScreen.style.display = 'none';
  perfilAlumnoActual = null;
}

const periodos = {
  'primaria': ['1er Grado', '2do Grado', '3er Grado', '4to Grado', '5to Grado', '6to Grado'],
  'prescolar': ['2do Nivel', '3er Nivel'],
  'bachillerato': ['1er A\u00f1o', '2do A\u00f1o', '3er A\u00f1o', '4to A\u00f1o', '5to A\u00f1o']
};

const sequenceOfPeriodos = [
  '2do Nivel', '3er Nivel',
  '1er Grado', '2do Grado', '3er Grado', '4to Grado', '5to Grado', '6to Grado',
  '1er A\u00f1o', '2do A\u00f1o', '3er A\u00f1o', '4to A\u00f1o', '5to A\u00f1o'
];

let perfilAlumnoActual = null;

async function openPerfil(alumnoId) {
  const alumno = students.find(s => s.id === alumnoId);
  if (!alumno) return;
  
  perfilAlumnoActual = alumno;
  
  // Llenar datos del perfil
  $('perfilNombreCompleto').textContent = alumno.nombre + ' ' + alumno.apellido;
  $('perfilCedula').textContent = alumno.cedula;
  $('perfilNivel').textContent = levelNames[alumno.level] || alumno.level;
  $('perfilTipo').textContent = alumno.tipo === 'Nuevo Ingreso' 
    ? `Nuevo Ingreso (${alumno.ingreso_periodo})` 
    : (alumno.tipo || 'Regular');
  
  const estadoEl = $('perfilEstado');
  estadoEl.textContent = alumno.status || 'Activo';
  if (alumno.status === 'Activo') {
    estadoEl.style.color = '#10b981';
  } else {
    estadoEl.style.color = '#f59e0b';
  }

  // Vivienda
  $('perfilDireccion').textContent = alumno.direccion || 'No registrada';
  $('perfilCiudad').textContent = alumno.ciudad || 'No registrada';
  $('perfilEstadoRes').textContent = alumno.estado_residencia || 'No registrado';
  $('perfilTelefono').textContent = alumno.telefono_casa || 'No registrado';

  // Render familiares (se cargan del backend)
  const famListEl = $('perfilFamiliaresList');
  famListEl.innerHTML = '<p style="color:#6b7280;"><i class="fas fa-spinner fa-spin"></i> Cargando familiares...</p>';

  eel.get_familiares(alumnoId)().then(famRes => {
    if (famRes.success && famRes.familiares && famRes.familiares.length > 0) {
      famListEl.innerHTML = famRes.familiares.map(f => `
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px;display:grid;grid-template-columns:repeat(auto-fit, minmax(140px, 1fr));gap:12px;align-items:center;">
          <div>
            <span style="font-size:0.75rem;text-transform:uppercase;color:#64748b;font-weight:600;display:block;">Familiar / Parentesco</span>
            <strong style="color:#1e293b;font-size:0.9rem;">${f.parentesco}</strong>
          </div>
          <div>
            <span style="font-size:0.75rem;text-transform:uppercase;color:#64748b;font-weight:600;display:block;">Nombre Completo</span>
            <span style="color:#334155;font-size:0.9rem;">${f.nombre} ${f.apellido}</span>
          </div>
          <div>
            <span style="font-size:0.75rem;text-transform:uppercase;color:#64748b;font-weight:600;display:block;">Cédula</span>
            <span style="color:#334155;font-size:0.9rem;">${f.cedula || 'No registrada'}</span>
          </div>
          <div>
            <span style="font-size:0.75rem;text-transform:uppercase;color:#64748b;font-weight:600;display:block;">Teléfono</span>
            <span style="color:#334155;font-size:0.9rem;">${f.telefono || 'No registrado'}</span>
          </div>
        </div>
      `).join('');
    } else {
      famListEl.innerHTML = `
        <div style="padding:15px;text-align:center;color:#6b7280;background:#f3f4f6;border-radius:10px;font-size:0.9rem;">
          No hay familiares ni representantes registrados para este alumno.
        </div>`;
    }
  }).catch(err => {
    famListEl.innerHTML = `<p style="color:#ef4444;font-size:0.9rem;">Error al cargar familiares</p>`;
  });

  perfilScreen.style.display = 'block';
  perfilScreen.scrollTop = 0;
  
  // Cargar notas
  const notasContainer = $('perfilNotas');
  notasContainer.innerHTML = '<p style="color:#6b7280;"><i class="fas fa-spinner fa-spin"></i> Cargando archivos...</p>';
  
  const res = await eel.get_notas(alumnoId)();
  const notasSubidas = res.success ? res.notas : {};
  
  // Determinar la lista de periodos
  let perList = [];
  let entryIdx = -1;
  
  if (alumno.tipo === 'Egresado') {
    perList = ['Notas Totales'];
  } else if (alumno.tipo === 'Nuevo Ingreso' || alumno.tipo === 'Regular') {
    const fullList = periodos[alumno.level] || [];
    entryIdx = fullList.indexOf(alumno.ingreso_periodo);
    
    const seqIdx = sequenceOfPeriodos.indexOf(alumno.ingreso_periodo);
    if (seqIdx > 0) {
      const prevPeriod = sequenceOfPeriodos[seqIdx - 1];
      if (!fullList.includes(prevPeriod)) {
        perList = [prevPeriod, ...fullList];
        entryIdx = 1;
      } else {
        perList = fullList;
      }
    } else {
      perList = fullList;
    }
  } else {
    perList = periodos[alumno.level] || [];
  }
  
  notasContainer.innerHTML = '';
  let hasAnyNote = false;

  // ——— For primaria/prescolar Regular/Nuevo Ingreso: show previous year note + current year upload ———
  const isPriPre = (alumno.level === 'primaria' || alumno.level === 'prescolar') &&
                   (alumno.tipo === 'Regular' || alumno.tipo === 'Nuevo Ingreso') &&
                   alumno.ingreso_periodo;

  if (isPriPre) {
    // Previous year note (read-only view + year before in sequence)
    const seqIdx2 = sequenceOfPeriodos.indexOf(alumno.ingreso_periodo);
    const prevPeriod = seqIdx2 > 0 ? sequenceOfPeriodos[seqIdx2 - 1] : null;
    
    if (prevPeriod) {
      const prevNota = notasSubidas[prevPeriod];
      const prevTiene = !!prevNota;
      if (prevTiene) hasAnyNote = true;
      const prevArchivo = prevTiene ? prevNota.archivo : null;
      const prevAnio = prevTiene && prevNota.anio ? ` (Año: ${prevNota.anio})` : '';
      const prevBadge = prevTiene
        ? `<span style="color:#10b981;font-size:0.85em;"><i class="fas fa-check-circle"></i> ${prevArchivo}${prevAnio}</span>`
        : '<span style="color:#9ca3af;font-size:0.85em;"><i class="fas fa-times-circle"></i> Sin archivo</span>';
      const prevVerBtn = prevTiene
        ? `<button onclick="verArchivo(${alumnoId}, '${prevPeriod}')" style="background:#10b981;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;"><i class="fa-solid fa-eye"></i> Ver</button>`
        : '';
      
      const prevRow = document.createElement('div');
      prevRow.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;';
      prevRow.innerHTML = `
        <div>
          <span style="font-weight:600;color:#374151;">${prevPeriod}
            <span style="background:#6b7280;color:white;padding:2px 6px;border-radius:4px;font-size:0.75rem;margin-left:8px;font-weight:normal;">Año Anterior</span>
          </span><br>
          <small>${prevBadge}</small>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          ${prevVerBtn}
          <input type="text" id="panio_${alumnoId}_${prevPeriod.replace(/[^a-zA-Z0-9]/g, '_')}" data-periodo="${prevPeriod}" placeholder="Año" style="width:70px;padding:4px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:0.85rem;" value="${prevTiene && prevNota.anio ? prevNota.anio : new Date().getFullYear()}" disabled class="anio-input">
          <input type="file" id="pfile_${alumnoId}_${prevPeriod.replace(/[^a-zA-Z0-9]/g, '_')}" style="display:none;" onchange="uploadFileFromPerfil(${alumnoId}, '${prevPeriod}', this)">
          <button onclick="document.getElementById('pfile_${alumnoId}_${prevPeriod.replace(/[^a-zA-Z0-9]/g, '_')}').click()" style="background:#4f46e5;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;">
            <i class="fas fa-upload"></i> ${prevTiene ? 'Reemplazar' : 'Subir'}
          </button>
        </div>
      `;
      notasContainer.appendChild(prevRow);
    }

    // Current year note upload
    const curPeriod = alumno.ingreso_periodo;
    const curNota = notasSubidas[curPeriod];
    const curTiene = !!curNota;
    if (curTiene) hasAnyNote = true;
    const curArchivo = curTiene ? curNota.archivo : null;
    const curAnio = curTiene && curNota.anio ? ` (Año: ${curNota.anio})` : '';
    const curBadge = curTiene
      ? `<span style="color:#10b981;font-size:0.85em;"><i class="fas fa-check-circle"></i> ${curArchivo}${curAnio}</span>`
      : '<span style="color:#ef4444;font-size:0.85em;"><i class="fas fa-exclamation-circle"></i> Pendiente de subir</span>';
    const curVerBtn = curTiene
      ? `<button onclick="verArchivo(${alumnoId}, '${curPeriod}')" style="background:#10b981;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;"><i class="fa-solid fa-eye"></i> Ver</button>`
      : '';

    const curRow = document.createElement('div');
    curRow.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#eff6ff;border:2px solid #4f46e5;border-radius:10px;';
    curRow.innerHTML = `
      <div>
        <span style="font-weight:600;color:#374151;">${curPeriod}
          <span style="background:#4f46e5;color:white;padding:2px 6px;border-radius:4px;font-size:0.75rem;margin-left:8px;font-weight:normal;">Año Actual ✦</span>
        </span><br>
        <small>${curBadge}</small>
        <small style="display:block;color:#6b7280;margin-top:3px;font-size:0.78rem;">Al subir esta nota, pasará a ser el año anterior y el alumno avanzará al siguiente grado.</small>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        ${curVerBtn}
        <input type="text" id="panio_${alumnoId}_${curPeriod.replace(/[^a-zA-Z0-9]/g, '_')}" data-periodo="${curPeriod}" placeholder="Año" style="width:70px;padding:4px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:0.85rem;" value="${curTiene && curNota.anio ? curNota.anio : new Date().getFullYear()}" disabled class="anio-input">
        <input type="file" id="pfile_${alumnoId}_${curPeriod.replace(/[^a-zA-Z0-9]/g, '_')}" style="display:none;" onchange="uploadFileFromPerfil(${alumnoId}, '${curPeriod}', this, true)">
        <button onclick="document.getElementById('pfile_${alumnoId}_${curPeriod.replace(/[^a-zA-Z0-9]/g, '_')}').click()" style="background:#4f46e5;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;font-weight:600;">
          <i class="fas fa-upload"></i> ${curTiene ? 'Reemplazar' : 'Subir Nota Actual'}
        </button>
      </div>
    `;
    notasContainer.appendChild(curRow);

  } else {
    // ——— Default rendering for all other cases ———
    for (let i = 0; i < perList.length; i++) {
      const p = perList[i];
      const notaInfo = notasSubidas[p];
      const tieneNota = !!notaInfo;
      if (tieneNota) hasAnyNote = true;
      const nombreArchivo = tieneNota ? notaInfo.archivo : null;
      const anio = tieneNota && notaInfo.anio ? ` (Año: ${notaInfo.anio})` : '';

      let labelPrefix = '';
      let badge = '';
      
      badge = tieneNota
        ? `<span style="color:#10b981;font-size:0.85em;"><i class="fas fa-check-circle"></i> ${nombreArchivo}${anio}</span>`
        : '<span style="color:#9ca3af;font-size:0.85em;"><i class="fas fa-times-circle"></i> Sin archivo</span>';
      
      const verBtn = tieneNota
        ? `<button onclick="verArchivo(${alumnoId}, '${p}')" style="background:#10b981;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;">
             <i class="fa-solid fa-eye"></i> Ver
           </button>`
        : '';

      const row = document.createElement('div');
      row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;';
      row.innerHTML = `
        <div>
          <span style="font-weight:600;color:#374151;">${p}${labelPrefix}</span><br>
          <small>${badge}</small>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          ${verBtn}
          <input type="text" id="panio_${alumnoId}_${p.replace(/[^a-zA-Z0-9]/g, '_')}" data-periodo="${p}" placeholder="Año" style="width:70px;padding:4px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:0.85rem;" value="${tieneNota && notaInfo.anio ? notaInfo.anio : new Date().getFullYear()}" disabled class="anio-input">
          <input type="file" id="pfile_${alumnoId}_${p.replace(/[^a-zA-Z0-9]/g, '_')}" style="display:none;" onchange="uploadFileFromPerfil(${alumnoId}, '${p}', this)">
          <button onclick="document.getElementById('pfile_${alumnoId}_${p.replace(/[^a-zA-Z0-9]/g, '_')}').click()" style="background:#4f46e5;color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:0.85rem;">
            <i class="fas fa-upload"></i> Subir
          </button>
        </div>
      `;
      notasContainer.appendChild(row);
    }
  }

  const btnEditAnios = document.getElementById('btnEditAnios');
  if (btnEditAnios) {
    btnEditAnios.style.display = hasAnyNote ? 'inline-block' : 'none';
    btnEditAnios.innerHTML = '<i class="fas fa-edit"></i> Editar Años';
    btnEditAnios.dataset.editing = 'false';
  }
}

async function toggleEditAnios() {
  const btn = document.getElementById('btnEditAnios');
  if (!btn || !perfilAlumnoActual) return;
  const isEditing = btn.dataset.editing === 'true';

  const inputs = document.querySelectorAll('#perfilNotas .anio-input');
  
  if (!isEditing) {
    // Enable editing
    btn.dataset.editing = 'true';
    btn.innerHTML = '<i class="fas fa-save"></i> Guardar Años';
    btn.style.background = '#10b981';
    inputs.forEach(input => input.disabled = false);
  } else {
    // Save changes
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    
    const periodosAnios = {};
    inputs.forEach(input => {
      periodosAnios[input.dataset.periodo] = input.value.trim();
    });

    const res = await eel.update_anios(perfilAlumnoActual.id, periodosAnios)();
    
    btn.disabled = false;
    if (res.success) {
      openPerfil(perfilAlumnoActual.id);
    } else {
      alert('Error guardando años: ' + res.error);
      btn.dataset.editing = 'false';
      btn.innerHTML = '<i class="fas fa-edit"></i> Editar Años';
      btn.style.background = '#f59e0b';
      inputs.forEach(input => input.disabled = true);
    }
  }
}

async function deleteFromProfile() {
  if (!perfilAlumnoActual) return;
  if (!confirm('¿Eliminar a ' + perfilAlumnoActual.nombre + ' ' + perfilAlumnoActual.apellido + ' y todos sus archivos?')) return;
  const res = await eel.delete_alumno(parseInt(perfilAlumnoActual.id))();
  if (res.success) {
    closePerfilScreen();
    renderDashboard();
  } else {
    alert('Error al eliminar: ' + res.error);
  }
}

async function uploadFileFromPerfil(alumnoId, periodo, inputEl, isCurrentYear = false) {
  const file = inputEl.files[0];
  if (!file) return;

  if (isCurrentYear) {
    const confirmed = confirm(
      `¿Confirmar subida de nota para "${periodo}"?\n\n` +
      `Al confirmar:\n` +
      `• Esta nota pasará a ser la nota del año anterior.\n` +
      `• La nota anterior se eliminará automáticamente.\n` +
      `• El alumno avanzará al siguiente grado.`
    );
    if (!confirmed) return;
  }

  const anioInputId = `panio_${alumnoId}_${periodo.replace(/[^a-zA-Z0-9]/g, '_')}`;
  const anioInput = document.getElementById(anioInputId);
  const anio = anioInput ? anioInput.value.trim() : new Date().getFullYear().toString();

  const reader = new FileReader();
  reader.onload = async function() {
    const base64 = reader.result;
    const parentDiv = inputEl.closest('div[style]');
    const uploadBtn = parentDiv ? Array.from(parentDiv.querySelectorAll('button')).pop() : null;
    if (uploadBtn) uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    const res = await eel.upload_nota(alumnoId, periodo, base64, file.name, anio)();
    if (res.success) {
      // Reload student list so the new ingreso_periodo/nivel is reflected
      const updated = await eel.get_alumnos(null)();
      students = updated;
      // Find the (possibly promoted) student by id and reopen their profile
      const freshAlumno = students.find(s => s.id === alumnoId);
      if (freshAlumno) {
        perfilAlumnoActual = freshAlumno;
      }
      openPerfil(alumnoId);
    } else {
      alert('Error subiendo el archivo: ' + res.error);
    }
  };
  reader.readAsDataURL(file);
}

async function verArchivo(alumnoId, periodo) {
  const res = await eel.open_nota_file(alumnoId, periodo)();
  if (!res.success) {
    alert('No se pudo abrir el archivo: ' + res.error);
  }
}

// ============ HAMBURGER ============
hamburger.addEventListener('click', () => {
  sidebar.classList.toggle('open');
});

document.addEventListener('click', (e) => {
  if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !hamburger.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});

// ============ INIT ============
showScreen('login');
