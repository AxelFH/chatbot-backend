# flowchart_mapping.py

FLOWCHART_MAPPING = {
    "NA": {
        "keywords": [],
        "children": {
            "P": {
                "keywords": ["productos", "protocolos"],
                "children": {
                    "V": {
                        "keywords": ["vida"],
                        "children": {
                            "VR": {"keywords": ["beneficio", "premio", "recompensa","santander"]},
                            "IF": {"keywords": ["ingreso familiar", "familia", "ingresos", "seguro familiar","santander"]},
                            "VM": {"keywords": ["multianual", "a largo plazo", "plazo múltiple"]},
                        }
                    },
                    "PE": {
                        "keywords": ["pertenencias", "propiedades", "posesiones"],
                        "children": {
                            "BT": {"keywords": ["blindaje total", "protección", "completo","blindaje"]},
                        }
                    },
                    "A": {
                        "keywords": ["ahorro"],
                        "children": {
                            "OP": {"keywords": ["objetivo protegido", "meta segura", "objetivo seguro","santander"]},
                            "PF": {"keywords": ["plan futuro", "planificación futura", "futuro asegurado","santander"]},
                        }
                    },
                    "Py": {
                        "keywords": ["pymes", "pequeñas y medianas", "negocios", "comercios", "empresas"],
                        "children": {
                            "EPZ": {"keywords": ["protegida", "zurich"]},
                            "EPF": {"keywords": ["protegida", "flex"]},
                            "SBSPy": {"keywords": ["blindaje", "protección","santander"]},
                            "CS": {"keywords": ["ciberseguridad", "seguridad cibernética", "protección digital"]},
                        }
                    },
                    "GM": {
                        "keywords": [],
                        "children": {
                            "GMS": {"keywords": ["gastos médicos", "salud","santander", "cobertura médica"]},
                        }
                    },
                    "HO": {
                        "keywords": [],
                        "children": {
                            "HP": {"keywords": ["hogar", "casa", "vivienda"]},
                        }
                    },
                }
            }
        }
    }
}


MINI_FLOWCHART_MAPPING = {
    "ASN": {
        "keywords": ["acceso segneurona","segneurona"],
        "children": {
            "CENE": {"keywords": ["clave","ejecutivo","no existe", "no aparece"]},
            "SNDA": {"keywords": ["sucursal no dada  alta", "no dada  alta   sistema","sucursal no existe","sucursal"]},
            "UR": {"keywords": ["Usuario Reciclado", "Reciclado", "Usuario Repetido","Copia  usuario","Nombre  ejecutivo diferente"]},
            "ENI": {"keywords": ["ejectivo","nuevo ingreso","alta ejecutivo","alta usuario","crear usuario"]}
        }
    },
    "CT": {
        "keywords": ["cotización"],
        "children": {
            "EX75": {"keywords": ["excede 75 caracteres permitidos", "caracter","excede","maximo"]},
            "ASL": {"keywords": ["asesoría para llenar formulario","llenado  formularios","formulario  cotización","formulario","busco asesoria para un formulario"]},
            "EDP": {"keywords": ["primas"]},
            "ELC": {"keywords": ["se ha excedido  límite  cúmulos","limite  cumulos"]},
            "NPA": {"keywords": ["agregar asegurados","problema asegurados","alta asegurados"]},
            "MVO": {"keywords": ["validación","OII"]},
            "MVNF": {"keywords": ["validación","Negative File","en ingles"]},
            "MTEST": {"keywords": ["test","Test","prueba"]}
        }
    }
}