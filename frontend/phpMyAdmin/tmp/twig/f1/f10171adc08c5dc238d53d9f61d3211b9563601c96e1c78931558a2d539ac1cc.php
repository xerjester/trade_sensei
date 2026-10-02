<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Extension\SandboxExtension;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* server/engines/show.twig */
class __TwigTemplate_ae32cf876d9c5d1c46d80365ffccabcc0c54ff085bd2dbdf5644b2b986d63232 extends \Twig\Template
{
    private $source;
    private $macros = [];

    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->source = $this->getSourceContext();

        $this->parent = false;

        $this->blocks = [
        ];
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 1
        echo "<h2>
  ";
        // line 2
        echo \PhpMyAdmin\Html\Generator::getImage("b_engine");
        echo "
  ";
        // line 3
        echo _gettext("Storage engines");
        // line 4
        echo "</h2>

";
        // line 6
        if ( !twig_test_empty(($context["engine"] ?? null))) {
            // line 7
            echo "  <h2>
    ";
            // line 8
            echo \PhpMyAdmin\Html\Generator::getImage("b_engine");
            echo "
    ";
            // line 9
            echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "title", [], "any", false, false, false, 9), "html", null, true);
            echo "
    ";
            // line 10
            echo \PhpMyAdmin\Html\MySQLDocumentation::show(twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "help_page", [], "any", false, false, false, 10));
            echo "
  </h2>
  <p><em>";
            // line 12
            echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "comment", [], "any", false, false, false, 12), "html", null, true);
            echo "</em></p>

  ";
            // line 14
            if (( !twig_test_empty(twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "info_pages", [], "any", false, false, false, 14)) && twig_test_iterable(twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "info_pages", [], "any", false, false, false, 14)))) {
                // line 15
                echo "    <p>
      <strong>[</strong>
      ";
                // line 17
                if (twig_test_empty(($context["page"] ?? null))) {
                    // line 18
                    echo "        <strong>";
                    echo _gettext("Variables");
                    echo "</strong>
      ";
                } else {
                    // line 20
                    echo "        <a href=\"";
                    echo PhpMyAdmin\Url::getFromRoute(("/server/engines/" . twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "engine", [], "any", false, false, false, 20)));
                    echo "\">
          ";
                    // line 21
                    echo _gettext("Variables");
                    // line 22
                    echo "        </a>
      ";
                }
                // line 24
                echo "      ";
                $context['_parent'] = $context;
                $context['_seq'] = twig_ensure_traversable(twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "info_pages", [], "any", false, false, false, 24));
                foreach ($context['_seq'] as $context["current"] => $context["label"]) {
                    // line 25
                    echo "        <strong>|</strong>
        ";
                    // line 26
                    if ((array_key_exists("page", $context) && (($context["page"] ?? null) == $context["current"]))) {
                        // line 27
                        echo "          <strong>";
                        echo twig_escape_filter($this->env, $context["label"], "html", null, true);
                        echo "</strong>
        ";
                    } else {
                        // line 29
                        echo "          <a href=\"";
                        echo PhpMyAdmin\Url::getFromRoute(((("/server/engines/" . twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "engine", [], "any", false, false, false, 29)) . "/") . $context["current"]));
                        echo "\">
            ";
                        // line 30
                        echo twig_escape_filter($this->env, $context["label"], "html", null, true);
                        echo "
          </a>
        ";
                    }
                    // line 33
                    echo "      ";
                }
                $_parent = $context['_parent'];
                unset($context['_seq'], $context['_iterated'], $context['current'], $context['label'], $context['_parent'], $context['loop']);
                $context = array_intersect_key($context, $_parent) + $_parent;
                // line 34
                echo "      <strong>]</strong>
    </p>
  ";
            }
            // line 37
            echo "
  ";
            // line 38
            if ( !twig_test_empty(twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "page", [], "any", false, false, false, 38))) {
                // line 39
                echo "    ";
                echo twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "page", [], "any", false, false, false, 39);
                echo "
  ";
            } else {
                // line 41
                echo "    <p>";
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "support", [], "any", false, false, false, 41), "html", null, true);
                echo "</p>
    ";
                // line 42
                echo twig_get_attribute($this->env, $this->source, ($context["engine"] ?? null), "variables", [], "any", false, false, false, 42);
                echo "
  ";
            }
        } else {
            // line 45
            echo "  <p>";
            echo call_user_func_array($this->env->getFilter('error')->getCallable(), [_gettext("Unknown storage engine.")]);
            echo "</p>
";
        }
    }

    public function getTemplateName()
    {
        return "server/engines/show.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  158 => 45,  152 => 42,  147 => 41,  141 => 39,  139 => 38,  136 => 37,  131 => 34,  125 => 33,  119 => 30,  114 => 29,  108 => 27,  106 => 26,  103 => 25,  98 => 24,  94 => 22,  92 => 21,  87 => 20,  81 => 18,  79 => 17,  75 => 15,  73 => 14,  68 => 12,  63 => 10,  59 => 9,  55 => 8,  52 => 7,  50 => 6,  46 => 4,  44 => 3,  40 => 2,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "server/engines/show.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\server\\engines\\show.twig");
    }
}
